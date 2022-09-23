import pandas as pd
import datetime
import numpy as np


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


def get_start_date(filename):
    with open(filename) as f:
        lines = f.readlines()

    idxs = [idx for idx, line in enumerate(
        lines) if 'Recording: Startdate' in line]
    idx = idxs[0] + 1

    _, date, _, time = lines[idx].split(' ')
    date = date + '_' + time.replace('\n', '')

    date = datetime.datetime.strptime(date, '%d.%m.%y_%H.%M.%S')

    return date


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
    start_date = get_start_date(filename)
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

        stage['date'] = start_date + datetime.timedelta(seconds=stage['t'])

    hyp_df = pd.DataFrame(data=stages)

    return hyp_df.copy()


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


def normalize_dataframe(df, settings, tolerance=45):
    if int(df['date'][df.index[0]].strftime('%M')) <= 60 - tolerance:
        df = pad_dataframe(df, settings)
    else:
        df = truncate_dataframe(df)

    if int(df['date'][df.index[-1]].strftime('%M')) >= tolerance:
        df = pad_dataframe(df, settings, flip=True)
    else:
        df = truncate_dataframe(df, flip=True)

    return df


def truncate_dataframe(df, flip: bool = False):
    if flip is False:
        h0 = int(df['date'][df.index[0]].strftime('%H'))

        for idx, value in df.iterrows():
            h = int(value['date'].strftime('%H'))
            if h != h0:
                df = df.truncate(before=idx)
                break
    else:
        h0 = int(df['date'][df.index[-1]].strftime('%H'))
        df = df.iloc[::-1]

        for idx, value in df.iterrows():
            h = int(value['date'].strftime('%H'))
            if h != h0:
                df = df.truncate(after=idx)
                break

        df = df.iloc[::-1]

    return df


def pad_dataframe(df, settings, flip: bool = False):
    h0 = df['date'][df.index[0]]
    h_end = df['date'][df.index[-1]]

    if flip is False:
        df_h = pd.DataFrame({'label': settings['hyp']['ignored_label'],
                             'date': pd.date_range(start=h0 - datetime.timedelta(hours=1), end=h0, freq=str(settings['hyp']['sampling_time']) + 'S')})
        df = pd.concat([df_h, df], ignore_index=True)
    else:
        df_h = pd.DataFrame({'label': settings['hyp']['ignored_label'],
                             'date': pd.date_range(start=h_end, end=h_end + datetime.timedelta(hours=1), freq=str(settings['hyp']['sampling_time']) + 'S')})
        df = pd.concat([df, df_h], ignore_index=True)

    df = truncate_dataframe(df, flip=flip)

    return df


def count_full_hours(df):
    hours = np.zeros(24)

    h0 = int(df['date'][df.index[0]].strftime('%H'))
    hours[h0] = 1

    for _, value in df.iterrows():
        h = int(value['date'].strftime('%H'))
        if h != h0:
            h0 = h
            hours[h0] = hours[h0] + 1

    return hours
