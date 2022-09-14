import os
import hyp.analysis as analysis
import json
import utils

def run():
    settings = json.load(open('./settings.json'))

    sub = settings['sub']
    ses = settings['ses']

    if (ses == 'all') or (ses == ['all']):
        ses = []
        path = os.path.join(settings['dataset_dir'], settings['eeg_subdir'].split('ses')[0].replace(
            '<SUB>', sub))

        for file in os.listdir(path):
            if file.endswith('w'):
                _, _ses = file.split('-')
                ses.append(_ses)

    if type(ses) is str:
        ses = [ses]

    for _ses in ses:
        run = settings['run']

        output_dir = utils.create_output_dir(settings['output_dir'], sub, _ses)

        labels = []
        unique_labels = []

        output = {}
        output['sub'] = sub
        output['ses'] = _ses
        output['overall'] = {}
        output['runs'] = {}

        path = os.path.join(settings['dataset_dir'], settings['eeg_subdir'].replace(
            '<SUB>', sub).replace('<SES>', _ses))

        if (run == 'all') or (run == ['all']):
            run = []
            for file in os.listdir(path):
                if file.endswith(settings['hyp_suffix']):
                    _, _, _, _run, _ = file.split('_')
                    _, _run = _run.split('-')
                    run.append(_run)

        if type(run) is str:
            run = [run]

        for _run in run:
            filename = settings['filename'] + settings['hyp_suffix']

            filename = filename.replace('<SUB>', sub).replace(
                '<SES>', _ses).replace('<RUN>', _run)
            filename = os.path.join(path, filename)

            # STATS
            _labels, _unique_labels = analysis.get_labels(filename)
            _stats = analysis.get_stats(_labels, _unique_labels)
            output['runs']['run-' + _run] = _stats

            for label in _unique_labels:
                try:
                    label.index(unique_labels)
                except:
                    unique_labels.append(label)

            labels.extend(_labels)

            # ANNOTATIONS
            df = analysis.get_hyp_df(filename, settings)

        stats = analysis.get_stats(labels, unique_labels)
        output['overall'] = stats

        filename, _ = settings['filename'].replace(
            '<SUB>', sub).replace('<SES>', _ses).split('_run')

        with open(os.path.join(output_dir, filename + '_stats.json'), 'w') as f:
            json.dump(output, f)
