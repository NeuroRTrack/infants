import gc
import matplotlib.pyplot as plt
import mne
import numpy as np
import os
import seaborn as sns
import utils
from tqdm.notebook import tqdm
from .metrics import get_iPLV, get_PLV, get_PLV_mean
from .preprocessing import preprocess_data, concat_epochs, get_epochs_from_annotations


def get_adjacent_epochs_idxs(epochs, sfreq, description='Wake', window_duration=180):
    adjacent_idxs = []

    window_size = int(np.round(window_duration * sfreq))

    descriptions = epochs.to_data_frame()['condition'].values.tolist()

    start_idx = 0 if descriptions[0] == description else None

    for idx, _description in enumerate(descriptions):
        if _description != description:
            start_idx = None
        elif _description == description:
            if start_idx is None:
                start_idx = idx
        
        if (start_idx is not None) and (idx - start_idx >= window_size):
            adjacent_idxs.append(range(start_idx, idx))
            start_idx = None
       
    out = np.array(adjacent_idxs)

    del adjacent_idxs 
    del descriptions
    del epochs
    gc.collect()

    return out

def run(settings):
    path = settings['general']['dataset_dir']

    sub = settings['general']['sub']
    sub = utils.check_all_setting(sub, 'sub', path, prefix='sub')

    data = {}

    for _sub in tqdm(sub, desc='Subjects', unit='sub'):
        path = os.path.join(settings['general']['dataset_dir'], settings['general']['eeg_subdir'].split('ses')[0].replace(
            '<SUB>', _sub))

        ses = settings['general']['ses']
        ses = utils.check_all_setting(ses, 'ses', path, suffix='w')

        for _ses in tqdm(ses, desc='Subject ' + _sub + ' - Sessions', leave='False', unit='ses'):
            path = os.path.join(settings['general']['dataset_dir'], settings['general']['eeg_subdir'].replace(
                '<SUB>', _sub).replace('<SES>', _ses))

            run = settings['general']['run']
            run = utils.check_all_setting(
                run, 'run', path, suffix=settings['eeg']['suffix'])

            output_dir = utils.create_output_dir(
                settings['general']['output_dir'], _sub, _ses)

            data[_ses] = []

            for _run in tqdm(run, desc='Subject ' + _sub + ' - Session ' + _ses + ' - Runs', leave=False, unit='run'):
                eeg_filename = utils.get_filename(
                    settings, _sub, _ses, _run, settings['eeg']['suffix'])
                eeg_filename = os.path.join(path, eeg_filename)

                annotations_dir = os.path.join(
                    output_dir, settings['hyp']['annotations_subdir'])

                ann_filename = utils.get_filename(
                    settings, _sub, _ses, _run, settings['hyp']['annotations_suffix'])
                ann_filename = os.path.join(annotations_dir, ann_filename)

                raw = preprocess_data(eeg_filename, ann_filename, settings)
                epochs = get_epochs_from_annotations(
                    raw, settings['hyp']['good_descriptions'], settings['hyp']['sampling_time'])
                
                if epochs is not None:
                    data[_ses].append(epochs)

                del raw
                del epochs
                gc.collect()

        if len(data) > 0:
            for _ses in ses:
                epochs = concat_epochs(data[_ses])
                data = np.array([(np.concatenate(epochs.get_data(), axis=1))])
                
                sfreq = epochs.info['sfreq']
                freq_min = settings['eeg']['PLV']['freq_min']
                freq_max = settings['eeg']['PLV']['freq_max']
                n_freqs = settings['eeg']['PLV']['n_freqs']
                freqs = np.linspace(freq_min, freq_max, num=n_freqs)
                
                QS_idxs = get_adjacent_epochs_idxs(epochs, sfreq, description='QuietSleep')
                print('QuietSleep - # windows: {}'.format(QS_idxs.shape[0]))

                AS_idxs = get_adjacent_epochs_idxs(epochs, sfreq, description='ActiveSleep')
                print('ActiveSleep - # windows: {}'.format(AS_idxs.shape[0]))

                W_idxs = get_adjacent_epochs_idxs(epochs, sfreq, description='Wake')
                print('Wake - # windows: {}'.format(W_idxs.shape[0]))

                del epochs
                gc.collect()

                labels = ['QS', 'AS', 'W']

                PLV_mean = {}
                PLV_mean[labels[0]] = np.zeros([n_freqs])
                PLV_mean[labels[1]] = np.zeros([n_freqs])
                PLV_mean[labels[2]] = np.zeros([n_freqs])

                for freq_idx, freq in tqdm(enumerate(freqs), total=n_freqs, desc='Frequencies', unit='freq'):
                    data_morlet = mne.time_frequency.tfr_array_morlet(data, sfreq, [freq], n_jobs=4)[0, :, 0, :]

                    for description_idx, windows in enumerate([QS_idxs, AS_idxs, W_idxs]):
                        iPLV = np.zeros([data_morlet.shape[0], data_morlet.shape[0]])

                        for window in windows:
                            iPLV = iPLV + get_iPLV(data_morlet[:, list(window)])

                        if windows.shape[0] > 0:
                            iPLV = iPLV / windows.shape[0]

                        # plt.figure()
                        # plt.clf()
                        # sns.heatmap(QS_iPLV, cmap='viridis')
                        # plt.title('Averaged iPLV - sub-{} - {:.2f} Hz'.format(_sub, freq))
                        # plt.show()

                        PLV_mean[labels[description_idx]][freq_idx] = get_PLV_mean(iPLV)
                        
                        del iPLV
                        gc.collect()
                    
                    del data_morlet
                    gc.collect()

                plt.figure()
                plt.clf()
                plt.plot(freqs, PLV_mean['QS'], label='QS')
                plt.plot(freqs, PLV_mean['AS'], label='AS')
                plt.plot(freqs, PLV_mean['W'], label='W')
                plt.legend()
                plt.show()

            # for event_id in list(epochs.event_id.keys()):
            #     fig = epochs[event_id].plot_psd(
            #         fmin=0.1, fmax=30, spatial_colors=False, method='welch')
            #     fig.axes[0].set_title(event_id)
