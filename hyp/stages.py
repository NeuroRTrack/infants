import pandas as pd
import datetime
from .time import get_start_date, parse_timestamp


def get_stages(filename):
    with open(filename) as f:
        lines = f.readlines()

    idx = lines.index('Hypnogram:\n')
    lines = lines[idx+1:]

    stages = []
    for line in lines:
        _, t, description = line.split('\t')
        description = description.replace('\n', '')
        stages.append({'t': t, 'description': description.lower()})

    return stages


def get_descriptions(filename):
    stages = get_stages(filename)

    descriptions = []
    unique_descriptions = []
    for stage in stages:
        descriptions.append(stage['description'])
        try:
            unique_descriptions.index(descriptions[-1])
        except:
            unique_descriptions.append(descriptions[-1])

    return descriptions, unique_descriptions


def get_hyp_df(filename, settings):
    stages = get_stages(filename)
    t0 = parse_timestamp(stages[0]['t'])

    for stage in stages:
        stage['t'] = parse_timestamp(stage['t']) - t0 if (parse_timestamp(
            stage['t']) - t0) >= 0 else parse_timestamp(stage['t']) - t0 + parse_timestamp('24:0:0.000')

        try:
            idx = list(map(lambda description: description.lower(),
                       settings['hyp']['good_descriptions'])).index(stage['description'])
            stage['description'] = settings['hyp']['good_descriptions'][idx]
        except:
            stage['description'] = settings['hyp']['ignored_description']

        stage['date'] = get_start_date(filename) + datetime.timedelta(seconds=stage['t'])

    hyp_df = pd.DataFrame(data=stages)

    return hyp_df.copy()


def get_annotations(filename, settings):
    hyp_df = get_hyp_df(filename, settings)

    annotations = hyp_df.rename(columns={'t': 'onset'})
    annotations['duration'] = settings['hyp']['sampling_time']
    annotations = annotations[['description', 'onset', 'duration']]

    return annotations
