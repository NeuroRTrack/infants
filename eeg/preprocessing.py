import mne
import numpy as np
import os
import utils
import warnings

def _get_referenced_channels_names(settings):
    anodes = settings['eeg']['montage']['anode']
    cathodes = settings['eeg']['montage']['cathode']

    ch_names = []

    for idx, _ in enumerate(anodes):
        ch_name = str(anodes[idx]) + '-' + str(cathodes[idx])
        ch_names.append(ch_name)

    return ch_names


def _check_already_referenced(raw, settings):
    is_referenced = False    

    referenced_ch_names = _get_referenced_channels_names(settings)
    idxs = mne.pick_channels(raw.ch_names, include=referenced_ch_names)

    if len(idxs) == len(referenced_ch_names):
        is_referenced = True

    return is_referenced


def preprocess_data(eeg_filename, ann_filename, settings):
    raw = None

    if os.path.isfile(ann_filename):
        raw = mne.io.read_raw_edf(
            eeg_filename, preload=True, infer_types=True, verbose=False)

        if _check_already_referenced(raw, settings) is False:
            raw = mne.set_bipolar_reference(raw, settings['eeg']['montage']['anode'],
                                            settings['eeg']['montage']['cathode'], verbose=False)

        raw = raw.pick_channels(_get_referenced_channels_names(settings))

        raw = raw.notch_filter(settings['eeg']['notch_freq'], verbose=False)

        with utils.IgnoreWarnings('MILLISECONDS'):
            annotations = mne.read_annotations(ann_filename)
            annotations = mne.Annotations(annotations.onset * 1e9, annotations.duration,
                                        annotations.description, orig_time=raw.info['meas_date'])

        raw = raw.set_annotations(annotations, emit_warning=False, verbose=False)
    else:
        warnings.warn(ann_filename + ' not found. Skipped.')

    return raw


def concat_epochs(epochs_list):
    with utils.IgnoreWarnings('Annotations'):
        concatenated_epochs = mne.concatenate_epochs(
            epochs_list, verbose=False)

    return concatenated_epochs


def get_epochs_from_annotations(raw, descriptions: str | list, chunk_duration):
    if type(descriptions) is str:
        descriptions = [descriptions]

    event_id = {}
    for idx in range(len(descriptions)):
        event_id[descriptions[idx]] = idx + 1

    try:
        events, event_id = mne.events_from_annotations(
            raw, event_id=event_id, chunk_duration=chunk_duration, verbose=False)

        epochs = mne.Epochs(raw, events, event_id=event_id, tmin=0,
                            tmax=chunk_duration, baseline=None, preload=True, verbose=False)
    except:
        epochs = None

    return epochs
