import matplotlib.pyplot as plt
import mne
import numpy as np
import os
import seaborn as sns
import utils
from tqdm.notebook import tqdm
from .metrics import get_iPLV, get_PLV
from .preprocessing import preprocess_data, concat_epochs, get_epochs_from_annotations


def get_adjacent_epochs_idxs(epochs, sfreq, description='Wake', window_duration=180):
    adjacent_idxs = []

    window_size = np.round(window_duration * sfreq)

    descriptions = epochs.to_data_frame()['condition'].values.tolist()

    start_idx = 0 if descriptions[0] == description else None

    for idx, _description in enumerate(descriptions):
        if _description != description:
            start_idx = None
        elif _description == description:
            if start_idx is None:
                start_idx = idx
        
        if (start_idx is not None) and (idx - start_idx >= window_size):
            adjacent_idxs.append(list(range(start_idx, idx)))
            start_idx = None

    return np.matrix(adjacent_idxs)

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

        if (epochs is not None) and (len(epochs) > 0):
            for _ses in ses:
                epochs = concat_epochs(data[_ses])
                sfreq = epochs.info['sfreq']
                
                QS_idxs = get_adjacent_epochs_idxs(epochs, sfreq, description='QuietSleep')
                print(QS_idxs.shape)

                data = np.array([(np.concatenate(epochs.get_data(), axis=1))])
                data = mne.time_frequency.tfr_array_morlet(data, sfreq, [2]).squeeze()
                print(type(data))
                print(data.shape)
                
                QS_data = np.squeeze([data[:, window_idxs] for window_idxs in QS_idxs])
                print(type(QS_data))
                print(QS_data.shape)

                temp = []
                temp2 = []
                for window in QS_data:
                    QS_iPLV = get_iPLV(window)
                    QS_PLV = get_PLV(window)
                    temp.append(QS_iPLV)
                    temp2.append(QS_PLV)
                    # plt.figure()
                    # plt.clf()
                    # sns.heatmap(QS_iPLV[:, :], cmap='viridis')
                    # plt.show()

                temp = np.mean(temp, axis=0)
                # print(np.shape(temp))
                plt.figure()
                plt.clf()
                sns.heatmap(temp[:, :], cmap='viridis')
                plt.show()

                temp2 = np.mean(temp2, axis=0)
                # print(np.shape(temp))
                plt.figure()
                plt.clf()
                sns.heatmap(temp2[:, :], cmap='viridis')
                plt.show()


                # QS_epoch = [np.concatenate(epochs['QuietSleep']._data, axis=1)]
                # AS_epoch = [np.concatenate(epochs['ActiveSleep']._data, axis=1)]
                
                # print(np.shape(QS_epoch))
                # print(np.shape(AS_epoch))

                # freqs = np.linspace(1, 20, num=20)

                # QS_iPLV = get_iPLV(QS_epoch, 512, freqs)
                # AS_iPLV = get_iPLV(AS_epoch, 512, freqs)

                # QS_iPLV_mean = get_PLV_mean(QS_iPLV)
                # AS_iPLV_mean = get_PLV_mean(AS_iPLV)

                # plt.figure()
                # plt.plot(freqs, QS_iPLV_mean, freqs, AS_iPLV_mean)
                # plt.show()
                # plt.legend(['QS', 'AS'])

                # plt.figure()
                # plt.clf()
                # sns.heatmap(QS_iPLV[:, :, 0], cmap='viridis')
                # plt.show()

            # for event_id in list(epochs.event_id.keys()):
            #     fig = epochs[event_id].plot_psd(
            #         fmin=0.1, fmax=30, spatial_colors=False, method='welch')
            #     fig.axes[0].set_title(event_id)
