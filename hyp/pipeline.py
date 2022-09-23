import os
import json
import utils
from .stages import get_descriptions, get_annotations
from .stats import get_stats


def run(settings):
    sub = settings['general']['sub']
    ses = settings['general']['ses']
    run = settings['general']['run']

    path = os.path.join(settings['general']['dataset_dir'], settings['general']['eeg_subdir'].split('ses')[0].replace(
        '<SUB>', sub))

    ses = utils.check_all_setting(ses, 'ses', 'w', path)

    for _ses in ses:
        output_dir = utils.create_output_dir(
            settings['general']['output_dir'], sub, _ses)

        descriptions = []
        unique_descriptions = []

        output = {}
        output['sub'] = sub
        output['ses'] = _ses
        output['overall'] = {}
        output['runs'] = {}

        path = os.path.join(settings['general']['dataset_dir'], settings['general']['eeg_subdir'].replace(
            '<SUB>', sub).replace('<SES>', _ses))

        run = utils.check_all_setting(
            run, 'run', settings['hyp']['suffix'], path)

        for _run in run:
            filename = utils.get_filename(
                settings, _ses, _run, settings['hyp']['suffix'])
            filename = os.path.join(path, filename)

            # STATS
            _descriptions, _unique_descriptions = get_descriptions(filename)
            _stats = get_stats(_descriptions, _unique_descriptions)
            output['runs']['run-' + _run] = _stats

            for description in _unique_descriptions:
                try:
                    description.index(unique_descriptions)
                except:
                    unique_descriptions.append(description)

            descriptions.extend(_descriptions)

            # ANNOTATIONS
            annotations = get_annotations(filename, settings)

            annotations_dir = os.path.join(
                output_dir, settings['hyp']['annotations_subdir'])
            if not os.path.exists(annotations_dir):
                os.makedirs(annotations_dir, exist_ok=False)

            filename = utils.get_filename(
                settings, _ses, _run, settings['hyp']['annotations_suffix'])

            annotations.to_csv(os.path.join(
                annotations_dir, filename), index=False)

        stats = get_stats(descriptions, unique_descriptions)
        output['overall'] = stats

        filename = utils.get_filename(settings, _ses, suffix='_stats.json')

        with open(os.path.join(output_dir, filename), 'w') as f:
            json.dump(output, f)
