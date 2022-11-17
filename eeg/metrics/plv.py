import mne
import numpy as np
import numpy.typing as npt

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


def get_cPLV(A: npt.ArrayLike, B: npt.ArrayLike = None):
    '''
    Complex Phase Locking Value (cPLV)

    Parameters
    ----------
    A : ArrayLike
        Time frequency data (n_channels, n_freqs, n_samples)
    B : ArrayLike, optional
        Time frequency data (n_channels, n_freqs, n_samples), by default None. If None the PLV is computed on pairs of electrodes of A.

    Returns
    -------
    cPLV : ArrayLike
        Complex Phase Locking Value (cPLV). The output is a complex-valued matrix (n_channels, n_channels).

    Raises
    ------
    ValueError
        If the number of samples of the matrix A is different from the number of samples of the matrix B the algorithm is unable to perform the matrix product 
    '''
    if B is None:
        B = np.copy(A)
    
    _, n_samples_A = A.shape
    _, n_samples_B = B.shape

    if n_samples_A == n_samples_B:
        n_samples = n_samples_A

    A_norm = np.divide(A, abs(A))
    B_norm = np.divide(B, abs(B))

    cPLV = np.divide(np.matmul(A_norm, np.conjugate(B_norm.T)), n_samples)

    else:
        raise ValueError('The number of samples of the matrices is different.')

    return cPLV


def get_PLV(A: npt.ArrayLike, B: npt.ArrayLike = None):
    '''
    Phase Locking Value (PLV)

    Parameters
    ----------
    A : ArrayLike
        Time frequency data (n_channels, n_samples)
    B : ArrayLike, optional
        Time frequency data (n_channels, n_samples), by default None. If B is None the PLV is computed on pairs of electrodes of A.

    Returns
    -------
    PLV : ArrayLike
        Phase Locking Value (PLV). The output is a real-valued matrix (n_channels, n_channels).
    '''
    cPLV = get_cPLV(A, B)
    PLV = np.abs(cPLV)

    return PLV


def get_iPLV(A: npt.ArrayLike, B: npt.ArrayLike = None):
    '''
    Imaginary Phase Locking Value (iPLV)

    Parameters
    ----------
    A : ArrayLike
        Time frequency data (n_channels, n_samples)
    B : ArrayLike, optional
        Time frequency data (n_channels, n_samples), by default None. If B is None the PLV is computed on pairs of electrodes of A.

    Returns
    -------
    iPLV : ArrayLike
        Imaginary Phase Locking Value (iPLV). The output is a real-valued matrix (n_channels, n_channels).
    '''
    cPLV = get_cPLV(A, B)
    iPLV = np.abs(np.imag(cPLV))

    return iPLV

def get_PLV_mean(PLV):
    triu_idxs = np.triu_indices_from(PLV[:, :, 0], k=1)
    PLV_mean = np.mean(PLV[triu_idxs[0], triu_idxs[1], :], axis=0)

    return PLV_mean