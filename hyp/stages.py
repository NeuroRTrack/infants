import datetime
import numpy as np
import pandas as pd
from .time import get_start_date, parse_timestamp, count_full_hours


def _read_stages(filename: str):
    '''
    Get all the stages contained into a hypnogram file.
    A stage is defined as the union of a description and its occurring time.

    Parameters
    ----------
    filename : str
        The full filename of the hypnogram file to open, including the path.

    Returns
    -------
    stages : list
        All the stages contained in the specified hypnogram.
    '''
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


def _parse_descriptions(df: pd.DataFrame, settings: dict, descriptions_column : str = 'description'):
    '''
    Parse all the descriptions present in the passed dataframe
    according to the desired descriptions specified in the settings.
    All the other descriptions are ignored.

    Parameters
    ----------
    df : DataFrame
        Any dataframe containing a column with the descriptions inside. 
    settings : dict
        The execution settings.
    descriptions_column : str, optional
        The descriptions column name of the dataframe.

    Returns
    -------
    out : DataFrame
        The specified dataframe with the updated descriptions column.
    '''
    for row_idx, row in df.iterrows():
        try:
            idx = list(map(lambda description: description.lower(),
                       settings['hyp']['good_descriptions'])).index(row[descriptions_column])
            df.at[row_idx, descriptions_column] = settings['hyp']['good_descriptions'][idx]
        except:
            df.at[row_idx, descriptions_column] = settings['hyp']['ignored_description']

    return df


def get_stages(filename: str, settings: dict = None):
    '''
    Build a Pandas dataframe representing all the stages present in
    a hypnogram file.

    Parameters
    ----------
    filename : str
        The full filename of the hypnogram file to open, including the path.
    settings : dict, optional
        The execution settings. If present it parses the descriptions.

    Returns
    -------
    stages : DataFrame
        A dataframe made of three columns, the time in seconds
        elapsed from the beginning of the hypnogram, the date and time of
        the stage and the description associated to it.
    '''
    stages = _read_stages(filename)
    t0 = parse_timestamp(stages[0]['t'])
    start_date = get_start_date(filename)

    for stage in stages:
        stage['t'] = parse_timestamp(stage['t']) - t0
        if stage['t'] < 0:
            stage['t'] = stage['t'] + parse_timestamp('24:0:0.000')

        stage['date'] = start_date + datetime.timedelta(seconds=stage['t'])

    stages = pd.DataFrame(data=stages)

    if settings is not None:
        stages = _parse_descriptions(stages, settings)

    return stages.copy()


def get_annotations(stages: pd.DataFrame, settings: dict):
    '''
    Convert the descriptions dataframe into the annotations one,
    ready to be applied to an EEG signal, according to the MNE library
    format.

    Parameters
    ----------
    stages : DataFrame
        A dataframe having stages as rows.
    settings : dict
        The execution settings.

    Returns
    -------
    annotations : DataFrame
        A dataframe having three columns with the stage description,
        onset time in seconds and its duration in seconds.
    '''
    stages = _parse_descriptions(stages, settings)

    annotations = stages.rename(columns={'t': 'onset'})
    annotations['duration'] = settings['hyp']['sampling_time']
    annotations = annotations[['description', 'onset', 'duration']]

    return annotations.copy()


def count_adjacent_stages_per_hour(df, settings, description: str = 'Wake', min_duration: float = 300):
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


def get_stage_cycle(df, settings, description: str = 'Wake', normalized=True, tolerance=45):
    if type(description) is str:
        description = [description]

    hours = count_full_hours(df, settings, tolerance)
    counts = np.zeros(24)

    for _, value in df.iterrows():
        h = int(value['date'].strftime('%H'))
        if (hours[h] != 0) and (value['description'] in description):
            counts[h] = counts[h] + 1

    if normalized is True:
        total_counts = np.zeros(24)
        h0 = df['date'][df.index[0]]
        h0 = h0 - datetime.timedelta(minutes=h0.minute, seconds=h0.second)

        h_end = df['date'][df.index[-1]]
        h_end = h_end - \
            datetime.timedelta(minutes=h0.minute,
                               seconds=h0.second) + datetime.timedelta(hours=1)

        while h0 < h_end:
            idx = h0.hour

            _df = df.loc[(df['date'] >= h0) & (
                df['date'] < h0 + datetime.timedelta(hours=1))]
            h0 = h0 + datetime.timedelta(hours=1)

            total_counts[idx] = total_counts[idx] + _df.shape[0]

        counts = np.divide(counts, total_counts, out=np.zeros_like(
            counts), where=total_counts != 0)

    return counts
