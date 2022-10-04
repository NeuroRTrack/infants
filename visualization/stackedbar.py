import matplotlib.pyplot as plt
import numpy as np
from utils import check_kwargs_list


def _parse_kwargs(x, **kwargs):
    kwargs_list = [
        {'key': 'align', 'default': 'center', 'type': str},
        {'key': 'ax', 'default': None, 'type': None},
        {'key': 'boxoff', 'default': True, 'type': bool},
        {'key': 'color', 'default': [None for _ in x], 'type': tuple},
        {'key': 'dpi', 'default': 100, 'type': float},
        {'key': 'edgecolor', 'default': [None for _ in x], 'type': tuple},
        {'key': 'figsize', 'default': (6, 3), 'type': tuple},
        {'key': 'labels', 'default': None, 'type': tuple},
        {'key': 'legend_anchor', 'default': None, 'type': tuple},
        {'key': 'linewidth', 'default': 0.25, 'type': float},
        {'key': 'num', 'default': None, 'type': str},
        {'key': 'title', 'default': 'Multibar Plot', 'type': str},
        {'key': 'width', 'default': 0.75, 'type': float},
        {'key': 'xlabel', 'default': None, 'type': str},
        {'key': 'xlim', 'default': None, 'type': tuple},
        {'key': 'xticks', 'default': None, 'type': tuple},
        {'key': 'ylabel', 'default': None, 'type': str},
        {'key': 'ylim', 'default': None, 'type': tuple},
        {'key': 'yticks', 'default': None, 'type': tuple}
    ]
    kwargs = check_kwargs_list(kwargs_list, **kwargs)

    return kwargs


def plot_stacked_bar(x, data, **kwargs):
    kwargs = _parse_kwargs(x, **kwargs)

    if kwargs.get('ax') is None:
        plt.figure(num=kwargs.get('num'), figsize=kwargs.get(
            'figsize'), dpi=kwargs.get('dpi'))
        ax = plt.gca()
    else:
        ax = kwargs.get('ax')

    for idx in range(np.shape(data)[0]):
        ax.bar(x, data[idx], color=kwargs.get('color')[idx], edgecolor=kwargs.get('edgecolor')[
               idx], bottom=np.sum(data[:idx], axis=0) if idx != 0 else None, align=kwargs.get('align'), width=kwargs.get('width'))

    ax.set_title(kwargs.get('title'))
    ax.set_xlabel(kwargs.get('xlabel'))
    ax.set_ylabel(kwargs.get('ylabel'))

    if kwargs.get('xticks') is not None:
        ax.set_xticks(kwargs.get('xticks'))
    if kwargs.get('yticks') is not None:
        ax.set_yticks(kwargs.get('yticks'))

    ax.set_xlim(kwargs.get('xlim'))
    ax.set_ylim(kwargs.get('ylim'))

    if kwargs.get('boxoff') is True:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    if kwargs.get('labels') is not None:
        ax.legend(kwargs.get('labels'), loc='upper right',
                  fontsize='small', bbox_to_anchor=kwargs.get('legend_anchor'))

    return
