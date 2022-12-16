import gc
import numpy as np


def get_CI(data, n_bootstraps=1000, percentiles=[2.5, 97.5], n_samples=100):
    bootstraps = np.zeros((n_bootstraps, n_samples))

    for bootstrap_idx in range(n_bootstraps):
        perm_idxs = np.random.randint(0, data.shape[0], n_samples)
        bootstraps[bootstrap_idx, :] = data[perm_idxs]

    effect_sizes = np.mean(bootstraps, axis=1)

    CI = np.percentile(effect_sizes, percentiles, axis=0)

    del bootstraps
    del effect_sizes
    gc.collect()

    return CI
