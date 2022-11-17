import os
import json
import utils
from .stages import get_stages, get_annotations
from .stats import get_stats


def run(settings):
    path = settings['general']['dataset_dir']

    sub = settings['general']['sub']
    sub = utils.check_all_setting(sub, 'sub', path, prefix='sub')

    for _sub in sub:
        path = os.path.join(settings['general']['dataset_dir'], settings['general']['eeg_subdir'].split('ses')[0].replace(
            '<SUB>', _sub))

        ses = settings['general']['ses']
        ses = utils.check_all_setting(ses, 'ses', path, suffix='w')

        for _ses in ses:
            path = os.path.join(settings['general']['dataset_dir'], settings['general']['eeg_subdir'].replace(
                '<SUB>', _sub).replace('<SES>', _ses))

            run = settings['general']['run']
            run = utils.check_all_setting(
                run, 'run', path, suffix=settings['hyp']['suffix'])

            output_dir = utils.create_output_dir(
                settings['general']['output_dir'], _sub, _ses)

            descriptions = []
            unique_descriptions = []

            output = {}
            output['sub'] = _sub
            output['ses'] = _ses
            output['overall'] = {}
            output['runs'] = {}

            for _run in run:
                filename = utils.get_filename(
                    settings, _sub, _ses, _run, settings['hyp']['suffix'])
                filename = os.path.join(path, filename)

                # STATS
                stages = get_stages(filename)

                _descriptions = stages['description'].tolist()
                _unique_descriptions = stages['description'].unique().tolist()
                _stats = get_stats(_descriptions, _unique_descriptions)
                output['runs']['run-' + _run] = _stats

                unique_descriptions.extend(_unique_descriptions)
                unique_descriptions = list(set(unique_descriptions))
                descriptions.extend(_descriptions)

                # ANNOTATIONS
                annotations = get_annotations(stages, settings)

                annotations_dir = os.path.join(
                    output_dir, settings['hyp']['annotations_subdir'])
                if not os.path.exists(annotations_dir):
                    os.makedirs(annotations_dir, exist_ok=False)

                filename = utils.get_filename(
                    settings, _sub, _ses, _run, settings['hyp']['annotations_suffix'])

                annotations.to_csv(os.path.join(
                    annotations_dir, filename), index=False)

            stats = get_stats(descriptions, unique_descriptions)
            output['overall'] = stats

            filename = utils.get_filename(
                settings, _sub, _ses, suffix='_stats.json')

            with open(os.path.join(output_dir, filename), 'w') as f:
                json.dump(output, f)
