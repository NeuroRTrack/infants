import os
import mne

def preprocess_data(eeg_filename, ann_filename, settings):
    raw = mne.io.read_raw_edf(eeg_filename, preload=True, infer_types=True, verbose=False)

    raw = mne.set_bipolar_reference(raw, settings['eeg']['montage']['anode'],
                                    settings['eeg']['montage']['cathode'], verbose=False)
    ch_names = raw.ch_names[-8:]
    raw = raw.pick_channels(ch_names)

    raw = raw.notch_filter(settings['eeg']['notch_freq'])

    return raw

