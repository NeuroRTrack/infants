import datetime
from tracemalloc import start
import numpy as np
import pandas as pd
from .time import get_start_date, parse_timestamp, count_full_hours


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


def count_stages_per_hour(df, settings, description : str = 'Wake', min_duration : float = 300):
    min_duration = round(min_duration/settings['hyp']['sampling_time'])
    counts = np.zeros(24)

    h0 = int(df['date'][df.index[0]].strftime('%H'))
    
    start_idx = 0 if df['description'][df.index[0]] == description else None

    for idx, value in df.iterrows():
        h = int(value['date'].strftime('%H'))
        if h != h0:
            if (start_idx is not None) and (idx - start_idx >= min_duration):
                counts[h0] = counts[h0] + 1
            if value['description'] == description: 
                start_idx = idx
            else:
                start_idx = None
            
            h0 = h
        else:
            if start_idx is not None:
                if (value['description'] != description) or (idx == len(df.index) - 1):
                    if idx - start_idx >= min_duration:
                        counts[h0] = counts[h0] + 1
                    start_idx = None
            else:
                if value['description'] == description:
                    start_idx = idx

    return counts


def get_stage_cycle(df, settings, description : str = 'Wake', tolerance = 45):
    hours = count_full_hours(df, settings, tolerance)
    counts = np.zeros(24)

    for _, value in df.iterrows():
        h = int(value['date'].strftime('%H'))
        if (hours[h] != 0) and (value['description'] == description):
            counts[h] = counts[h] + 1

    # TODO: normalizzare sul numero di samples in un'ora (così è tra 0 e 1)

    return counts