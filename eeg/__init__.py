import os
import json
import utils
import eeg.preprocessing as preprocessing

def run():
    settings = json.load(open('./settings.json'))

    sub = settings['general']['sub']
    ses = settings['general']['ses']
    data = {}

    path = os.path.join(settings['general']['dataset_dir'], settings['general']['eeg_subdir'].split('ses')[0].replace(
            '<SUB>', sub))
    
    ses = utils.check_all_setting(ses, 'ses', 'w', path)

    for _ses in ses:
        run = settings['general']['run']
        data[_ses] = []

        output_dir = utils.create_output_dir(settings['general']['output_dir'], sub, _ses)

        path = os.path.join(settings['general']['dataset_dir'], settings['general']['eeg_subdir'].replace(
            '<SUB>', sub).replace('<SES>', _ses))
        
        run = utils.check_all_setting(run, 'run', settings['eeg']['suffix'], path)

        for _run in run:
            eeg_filename = utils.get_filename(settings, _ses, _run, settings['eeg']['suffix'])
            eeg_filename = os.path.join(path, eeg_filename)

            annotations_dir = os.path.join(
                output_dir, settings['hyp']['annotations_subdir'])
            
            ann_filename = utils.get_filename(settings, _ses, _run, settings['hyp']['annotations_suffix'])
            ann_filename = os.path.join(annotations_dir, ann_filename)

            raw = preprocessing.preprocess_data(eeg_filename, ann_filename, settings)
            epochs = preprocessing.get_epochs_from_annotations(raw, settings['hyp']['good_labels'], settings['hyp']['sampling_time'])
            data[_ses].append(epochs)

        epochs = preprocessing.concat_epochs(data[_ses])

        for idx in range(len(epochs.event_id)):
            fig = epochs[idx].plot_psd(fmin=0.1, fmax=100, spatial_colors=False)
            fig.axes[0].set_title(list(epochs.event_id.keys())[idx])
