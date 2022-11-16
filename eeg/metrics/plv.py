import mne
import numpy as np

# def get_cPLV(data, sfreq, freqs):
#     morlet = mne.time_frequency.tfr_array_morlet(data, sfreq, freqs).squeeze()
#     n_channels, n_freqs, _ = morlet.shape
#     phase = np.angle(morlet)
#     cPLV = np.zeros([n_channels, n_channels, n_freqs], dtype=complex)

#     for freq_idx in range(n_freqs):
#         for ch_1 in range(n_channels - 1):
#             for ch_2 in range(ch_1 + 1, n_channels):
#                 dphase = phase[ch_1, freq_idx, :] - phase[ch_2, freq_idx, :]
#                 cPLV[ch_1, ch_2, freq_idx] = np.mean(np.exp(1j*dphase))

#         cPLV[:, :, freq_idx] = cPLV[:, :, freq_idx] + cPLV[:, :, freq_idx].T
        
#     diag_idxs = np.diag_indices_from(cPLV[:, :, 0])
#     cPLV[diag_idxs[0], diag_idxs[1], :] = 1

#     return cPLV

def get_cPLV(A, B = None):
    _, n_samples = A.shape
    if B is None:
        B = A
    
    A_norm = np.divide(A, abs(A))
    B_norm = np.divide(B, abs(B))

    cPLV = np.divide(np.matmul(A_norm, np.conjugate(B_norm.T)), n_samples)

    return cPLV

def get_PLV(A):
    cPLV = get_cPLV(A)
    PLV = np.abs(cPLV)

    return PLV

def get_iPLV(A):
    cPLV = get_cPLV(A)
    iPLV = np.abs(np.imag(cPLV))

    return iPLV

def get_PLV_mean(PLV):
    triu_idxs = np.triu_indices_from(PLV[:, :, 0], k=1)
    PLV_mean = np.mean(PLV[triu_idxs[0], triu_idxs[1], :], axis=0)

    return PLV_mean