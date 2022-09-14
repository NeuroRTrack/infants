from cProfile import label
import os
import pandas as pd
from datetime import datetime

def get_stages(filename):
    with open(filename) as f:
        lines = f.readlines()

    idx = lines.index('Hypnogram:\n')
    lines = lines[idx+1:]

    stages = []
    for line in lines:
        [stage_id, t, stage_label] = line.split('\t')
        stage_label = stage_label.replace('\n', '')
        stages.append({'t': t, 'label': stage_label.lower()})

    return stages

def get_labels(filename):
    stages = get_stages(filename)

    labels = []
    for stage in stages:
        labels.append(stage['label'])

    unique_labels = []
    for label in labels:
        try:
            unique_labels.index(label)
            pass
        except:
            unique_labels.append(label)

    return labels, unique_labels

def get_stats(labels, unique_labels):
    stats = {}

    for label in unique_labels:
        stats[label] = {}
        stats[label]['count'] = labels.count(label)
        stats[label]['perc'] = round(round(stats[label]['count'] / len(labels), 3) * 100, 1)

    return stats

def get_hyp_df(filename, settings):
    stages = get_stages(filename)

    t0 = parse_timestamp(stages[0]['t'])

    for stage in stages:
        stage['t'] = parse_timestamp(stage['t']) - t0

        try:
            idx = list(map(lambda label: label.lower(), settings['good_labels'])).index(stage['label'])
            stage['label'] = settings['good_labels'][idx]
        except:
            stage['label'] = settings['bad_label']
    
    df = pd.DataFrame(data=stages)

    return df

def parse_timestamp(str : str):
    str, ms = str.split('.')
    h, m, s = str.split(':')

    h = int(h)
    m = int(m)
    s = int(s)
    ms = int(ms)

    t = (h * 60 * 60 * 1000 + m * 60 * 1000 + s * 1000 + ms) / 1000

    return t
