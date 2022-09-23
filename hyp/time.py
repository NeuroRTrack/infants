import datetime
import numpy as np
import pandas as pd


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


def parse_timestamp(str: str):
    str, ms = str.split('.')
    h, m, s = str.split(':')

    h = int(h)
    m = int(m)
    s = int(s)
    ms = int(ms)

    t = (h * 60 * 60 * 1000 + m * 60 * 1000 + s * 1000 + ms) / 1000

    return t


def normalize_dataframe(df, settings, tolerance=45):
    if int(df['date'][df.index[0]].strftime('%M')) <= 60 - tolerance:
        df = _pad_dataframe(df, settings)
    else:
        df = _truncate_dataframe(df)

    if int(df['date'][df.index[-1]].strftime('%M')) >= tolerance:
        df = _pad_dataframe(df, settings, flip=True)
    else:
        df = _truncate_dataframe(df, flip=True)

    return df


def _truncate_dataframe(df, flip: bool = False):
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


def _pad_dataframe(df, settings, flip: bool = False):
    h0 = df['date'][df.index[0]]
    h_end = df['date'][df.index[-1]]

    if flip is False:
        df_h = pd.DataFrame({'description': settings['hyp']['ignored_description'],
                             'date': pd.date_range(start=h0 - datetime.timedelta(hours=1), end=h0, freq=str(settings['hyp']['sampling_time']) + 'S')})
        df = pd.concat([df_h, df], ignore_index=True)
    else:
        df_h = pd.DataFrame({'description': settings['hyp']['ignored_description'],
                             'date': pd.date_range(start=h_end, end=h_end + datetime.timedelta(hours=1), freq=str(settings['hyp']['sampling_time']) + 'S')})
        df = pd.concat([df, df_h], ignore_index=True)

    df = _truncate_dataframe(df, flip=flip)

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
