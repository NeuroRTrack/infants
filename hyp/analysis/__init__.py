import pandas as pd


def get_stages(filename):
    with open(filename) as f:
        lines = f.readlines()

    idx = lines.index('Hypnogram:\n')
    lines = lines[idx+1:]

    stages = []
    for line in lines:
        _, t, stage_label = line.split('\t')
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
        stats[label]['perc'] = round(
            round(stats[label]['count'] / len(labels), 3) * 100, 1)

    return stats


def get_hyp_df(filename, settings):
    stages = get_stages(filename)

    t0 = parse_timestamp(stages[0]['t'])

    for stage in stages:
        stage['t'] = parse_timestamp(stage['t']) - t0 if (parse_timestamp(
            stage['t']) - t0) >= 0 else parse_timestamp(stage['t']) - t0 + parse_timestamp('24:0:0.000')

        try:
            idx = list(map(lambda label: label.lower(),
                       settings['hyp']['good_labels'])).index(stage['label'])
            stage['label'] = settings['hyp']['good_labels'][idx]
        except:
            stage['label'] = settings['hyp']['ignored_label']

    hyp_df = pd.DataFrame(data=stages)

    return hyp_df


def parse_timestamp(str: str):
    str, ms = str.split('.')
    h, m, s = str.split(':')

    h = int(h)
    m = int(m)
    s = int(s)
    ms = int(ms)

    t = (h * 60 * 60 * 1000 + m * 60 * 1000 + s * 1000 + ms) / 1000

    return t


def get_annotations(filename, settings):
    hyp_df = get_hyp_df(filename, settings)

    annotations = hyp_df.rename(columns={'t': 'onset', 'label': 'description'})
    annotations['duration'] = settings['hyp']['sampling_time']
    annotations = annotations[['description', 'onset', 'duration']]

    return annotations
