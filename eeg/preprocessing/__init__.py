import mne
import utils


def preprocess_data(eeg_filename, ann_filename, settings):
    raw = mne.io.read_raw_edf(
        eeg_filename, preload=True, infer_types=True, verbose=False)

    raw = mne.set_bipolar_reference(raw, settings['eeg']['montage']['anode'],
                                    settings['eeg']['montage']['cathode'], verbose=False)
    ch_names = raw.ch_names[-8:]
    raw = raw.pick_channels(ch_names)

    raw = raw.notch_filter(settings['eeg']['notch_freq'], verbose=False)

    with utils.IgnoreWarnings('MILLISECONDS'):
        annotations = mne.read_annotations(ann_filename)
        annotations = mne.Annotations(annotations.onset * 1e9, annotations.duration,
                                      annotations.description, orig_time=raw.info['meas_date'])

    raw = raw.set_annotations(annotations, emit_warning=False, verbose=False)

    return raw
