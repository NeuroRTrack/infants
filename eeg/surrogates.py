import numpy as np
from numpy.lib.stride_tricks import as_strided

def _roll(data, shift):
    m = np.asarray(shift)
    data_roll = data[:, [*range(data.shape[1]), *range(data.shape[1] - 1)]].copy() #need `copy`
    strd_0, strd_1 = data_roll.strides
    n = data.shape[1]
    result = as_strided(data_roll, (*data.shape, n), (strd_0 ,strd_1, strd_1))

    return result[np.arange(data.shape[0]), (n-m) % n]

def get_surrogates(data, iterations = 1):
    n_channels = data.shape[0]
    n_samples = data.shape[1]

    surrogates = np.copy(data)

    for _ in iterations:
        shift = np.random.randint(0, n_samples, n_channels)
        surrogates = _roll(surrogates, shift)

    return surrogates