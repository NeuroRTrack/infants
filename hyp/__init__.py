import os
import hyp.analysis as analysis
import json
import utils


def run():
    settings = json.load(open('./settings.json'))

    sub = settings['general']['sub']
    ses = settings['general']['ses']

    if (ses == 'all') or (ses == ['all']):
        ses = []
        path = os.path.join(settings['general']['dataset_dir'], settings['general']['eeg_subdir'].split('ses')[0].replace(
            '<SUB>', sub))

        for file in os.listdir(path):
            if file.endswith('w'):
                _, _ses = file.split('-')
                ses.append(_ses)

    if type(ses) is str:
        ses = [ses]

    for _ses in ses:
        run = settings['general']['run']

        output_dir = utils.create_output_dir(settings['general']['output_dir'], sub, _ses)

        labels = []
        unique_labels = []

        output = {}
        output['sub'] = sub
        output['ses'] = _ses
        output['overall'] = {}
        output['runs'] = {}

        path = os.path.join(settings['general']['dataset_dir'], settings['general']['eeg_subdir'].replace(
            '<SUB>', sub).replace('<SES>', _ses))

        if (run == 'all') or (run == ['all']):
            run = []
            for file in os.listdir(path):
                if file.endswith(settings['hyp']['suffix']):
                    _, _, _, _run, _ = file.split('_')
                    _, _run = _run.split('-')
                    run.append(_run)

        if type(run) is str:
            run = [run]

        for _run in run:
            filename = utils.get_filename(settings, _ses, _run, settings['hyp']['suffix'])
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
            annotations = analysis.get_annotations(filename, settings)

            annotations_dir = os.path.join(
                output_dir, settings['hyp']['annotations_subdir'])
            if not os.path.exists(annotations_dir):
                os.makedirs(annotations_dir, exist_ok=False)

            filename = utils.get_filename(settings, _ses, _run, settings['hyp']['annotations_suffix'])

            annotations.to_csv(os.path.join(
                annotations_dir, filename), index=False)

        stats = analysis.get_stats(labels, unique_labels)
        output['overall'] = stats

        filename = utils.get_filename(settings, _ses, suffix='_stats.json')

        with open(os.path.join(output_dir, filename), 'w') as f:
            json.dump(output, f)
