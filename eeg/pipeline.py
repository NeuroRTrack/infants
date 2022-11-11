import matplotlib.pyplot as plt
import mne
import numpy as np
import os
import seaborn as sns
import utils
from tqdm.notebook import tqdm
from .preprocessing import preprocess_data, concat_epochs, get_epochs_from_annotations


def run(settings):
    path = settings['general']['dataset_dir']

    sub = settings['general']['sub']
    sub = utils.check_all_setting(sub, 'sub', path, prefix='sub')

    data = {}

    for _sub in tqdm(sub, desc='Subjects', unit='sub'):
        path = os.path.join(settings['general']['dataset_dir'], settings['general']['eeg_subdir'].split('ses')[0].replace(
            '<SUB>', _sub))

        ses = settings['general']['ses']
        ses = utils.check_all_setting(ses, 'ses', path, suffix='w')

        for _ses in tqdm(ses, desc='Subject ' + _sub + ' - Sessions', leave='False', unit='ses'):
            path = os.path.join(settings['general']['dataset_dir'], settings['general']['eeg_subdir'].replace(
                '<SUB>', _sub).replace('<SES>', _ses))

            run = settings['general']['run']
            run = utils.check_all_setting(
                run, 'run', path, suffix=settings['eeg']['suffix'])

            output_dir = utils.create_output_dir(
                settings['general']['output_dir'], _sub, _ses)

            data[_ses] = []

            for _run in tqdm(run, desc='Subject ' + _sub + ' - Session ' + _ses + ' - Runs', leave=False, unit='run'):
                eeg_filename = utils.get_filename(
                    settings, _sub, _ses, _run, settings['eeg']['suffix'])
                eeg_filename = os.path.join(path, eeg_filename)

                annotations_dir = os.path.join(
                    output_dir, settings['hyp']['annotations_subdir'])

                ann_filename = utils.get_filename(
                    settings, _sub, _ses, _run, settings['hyp']['annotations_suffix'])
                ann_filename = os.path.join(annotations_dir, ann_filename)

                raw = preprocess_data(eeg_filename, ann_filename, settings)
                epochs = get_epochs_from_annotations(
                    raw, settings['hyp']['good_descriptions'], settings['hyp']['sampling_time'])
                if epochs is not None:
                    data[_ses].append(epochs)

        if (epochs is not None) and (len(epochs) > 0):
            for _ses in ses:
                epochs = concat_epochs(data[_ses])

                QS_epoch = [np.concatenate(epochs['QuietSleep']._data, axis=1)]
                print(np.shape(QS_epoch))
                AS_epoch = [np.concatenate(epochs['ActiveSleep']._data, axis=1)]
                print(np.shape(AS_epoch))

                def cplv(morlet):
                    n_channels, n_freq, _ = morlet.shape
                    phase = np.angle(morlet)
                    cplv = np.zeros([n_channels, n_channels, n_freq], dtype=complex)

                    for freq in range(n_freq):
                        for ch_1 in range(n_channels - 1):
                            for ch_2 in range(ch_1 + 1, n_channels):
                                dphase = phase[ch_1, freq, :] - phase[ch_2, freq, :]
                                cplv[ch_1, ch_2, freq] = np.mean(np.exp(1j*dphase))

                    return cplv

            freq = np.linspace(2, 20, num=10)
            n_freq = len(freq)

            QS_morlet = mne.time_frequency.tfr_array_morlet(QS_epoch, 512, freq).squeeze()
            AS_morlet = mne.time_frequency.tfr_array_morlet(AS_epoch, 512, freq).squeeze()

            QS_cplv = cplv(QS_morlet)
            AS_cplv = cplv(AS_morlet)

            QS_iplv = np.abs(np.imag(QS_cplv))
            AS_iplv = np.abs(np.imag(AS_cplv))

            QS_iplv_mean = np.zeros(10)
            AS_iplv_mean = np.zeros(10)

            for _freq in range(n_freq):

                QS_iplv[:, :, _freq] = QS_iplv[:, :, _freq] + QS_iplv[:, :, _freq].T
                _QS_iplv = QS_iplv[:, :, _freq]
                QS_iplv_mean[_freq] = np.mean(_QS_iplv[np.nonzero(_QS_iplv)])

                AS_iplv[:, :, _freq] = AS_iplv[:, :, _freq] + AS_iplv[:, :, _freq].T
                _AS_iplv = AS_iplv[:, :, _freq]
                AS_iplv_mean[_freq] = np.mean(_AS_iplv[np.nonzero(_AS_iplv)])

            plt.clf()
            plt.plot(freq, QS_iplv_mean, freq, AS_iplv_mean)
            plt.show()
            plt.legend(['QS', 'AS'])


                # print(np.shape(QS_morlet))
                # QS_cplv = cplv(QS_morlet)

                # QS_iplv = np.abs(np.imag(QS_cplv))
                # QS_iplv[:, :, 0] = QS_iplv[:, :, 0] + QS_iplv[:, :, 0].T

                # print(np.nonzero(QS_iplv[:, :, 0]))
                # print(QS_iplv[np.nonzero(QS_iplv[:, :, 0]), 0])
                
                # QS_iplv0 = QS_iplv[:, :, 0]

                # print(np.mean(QS_iplv0[np.nonzero(QS_iplv0)]), )
                
                # plt.clf()
                # sns.heatmap(QS_iplv[:, :, 0])
                # plt.show()


                # for event_id in list(epochs.event_id.keys()):
                #     fig = epochs[event_id].plot_psd(
                #         fmin=0.1, fmax=30, spatial_colors=False, method='welch')
                #     fig.axes[0].set_title(event_id)
