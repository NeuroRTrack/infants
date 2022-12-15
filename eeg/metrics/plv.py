import gc
import mne
import numpy as np
import numpy.typing as npt


def get_cPLV(A: npt.ArrayLike, B: npt.ArrayLike = None):
    '''
    Complex Phase Locking Value (cPLV)

    Parameters
    ----------
    A : array_like
        Time frequency data (n_channels, n_freqs, n_samples)
    B : array_like, optional
        Time frequency data (n_channels, n_freqs, n_samples), by default None. If None the PLV is computed on pairs of electrodes of A.

    Returns
    -------
    cPLV : array_like
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

        A = np.divide(A, abs(A))
        B = np.divide(B, abs(B))

        cPLV = np.divide(np.matmul(A, np.conjugate(B.T)), n_samples)
    else:
        raise ValueError('The number of samples of the matrices is different.')
    
    del A
    del B
    gc.collect()

    return cPLV


def get_PLV(A: npt.ArrayLike, B: npt.ArrayLike = None):
    '''
    Phase Locking Value (PLV)

    Parameters
    ----------
    A : array_like
        Time frequency data (n_channels, n_samples)
    B : array_like, optional
        Time frequency data (n_channels, n_samples), by default None. If B is None the PLV is computed on pairs of electrodes of A.

    Returns
    -------
    PLV : array_like
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
    B : array_like, optional
        Time frequency data (n_channels, n_samples), by default None. If B is None the PLV is computed on pairs of electrodes of A.

    Returns
    -------
    iPLV : array_like
        Imaginary Phase Locking Value (iPLV). The output is a real-valued matrix (n_channels, n_channels).
    '''
    cPLV = get_cPLV(A, B)
    iPLV = np.abs(np.imag(cPLV))

    return iPLV


def get_PLV_mean(PLV : npt.ArrayLike, axis : int = 0):
    '''
    Return the mean value of a PLV matrix.\n
    If the input matrix is 2D, then a single value is computed.
    If the input matrix is 3D, then a 2D averaged PLV matrix may be computed as well.
    Note that a all 1s or all 0s diagonal is not taken into account when computing the
    mean value.

    Parameters
    ----------
    PLV : array_like
        Any matrix containing the PLV data.
        It can be 2D (n_channels, n_channels), not necessarily square, or
        3D, where the extra dimension is assumed to be trials or repetitions.
    axis : int, optional, default=0
        The axis along which the mean is to be perfromed.
        For 2D input matrices it is ignored, while 3D matrices are generally
        assumed in the form (n_trials, n_channels, n_channels), however the
        axis parameter allows flexibility about the input matrix shape.
        If None, thus a single mean value is returned also in the case
        of 3D matrices.

    Returns
    -------
    PLV_mean : array_like or float
        The computed PLV mean. If the input matrix is 2D, then a single
        mean value is computed, by taking into account the pairwise
        PLV values between the channels. If the input matrix is 3D,
        it is possible to compute also an average PLV matrix according to
        the specified axis.
    '''
    if len(PLV.shape) == 2:
        n_channels_A, n_channels_B = PLV.shape

        if (n_channels_A == n_channels_B) and (len(set(np.diag(PLV))) == 1) and (set(np.diag(PLV)) in [0, 1]):
            triu_idxs = np.triu_indices_from(PLV[:, :], k=1)
            PLV_mean = np.mean(PLV[triu_idxs[0], triu_idxs[1]])
        else:
            PLV_mean = np.mean(PLV)
    else:
       PLV_mean = np.mean(PLV, axis=axis)

    return PLV_mean
