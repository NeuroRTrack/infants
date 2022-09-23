import os
import utils
from tqdm.notebook import tqdm
from .preprocessing import preprocess_data, concat_epochs, get_epochs_from_annotations

def run(settings):
    sub = settings['general']['sub']
    ses = settings['general']['ses']
    data = {}

    path = os.path.join(settings['general']['dataset_dir'], settings['general']['eeg_subdir'].split('ses')[0].replace(
            '<SUB>', sub))
    
    ses = utils.check_all_setting(ses, 'ses', 'w', path)

    for _ses in tqdm(ses, desc='Sessions', unit='ses'):
        run = settings['general']['run']
        data[_ses] = []

        output_dir = utils.create_output_dir(settings['general']['output_dir'], sub, _ses)

        path = os.path.join(settings['general']['dataset_dir'], settings['general']['eeg_subdir'].replace(
            '<SUB>', sub).replace('<SES>', _ses))
        
        run = utils.check_all_setting(run, 'run', settings['eeg']['suffix'], path)

        for _run in tqdm(run, desc='Session ' + _ses + ' - Runs', leave=False, unit='run'):
            eeg_filename = utils.get_filename(settings, _ses, _run, settings['eeg']['suffix'])
            eeg_filename = os.path.join(path, eeg_filename)

            annotations_dir = os.path.join(
                output_dir, settings['hyp']['annotations_subdir'])
            
            ann_filename = utils.get_filename(settings, _ses, _run, settings['hyp']['annotations_suffix'])
            ann_filename = os.path.join(annotations_dir, ann_filename)

            raw = preprocess_data(eeg_filename, ann_filename, settings)
            epochs = get_epochs_from_annotations(raw, settings['hyp']['good_descriptions'], settings['hyp']['sampling_time'])
            if epochs is not None: data[_ses].append(epochs)

    if (epochs is not None) and (len(epochs) > 0):
        for _ses in ses:
            epochs = concat_epochs(data[_ses])

            for idx in range(len(epochs.event_id)):
                fig = epochs[idx].plot_psd(fmin=0.1, fmax=100, spatial_colors=False)
                fig.axes[0].set_title(list(epochs.event_id.keys())[idx])
