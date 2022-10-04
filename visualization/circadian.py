import matplotlib.pyplot as plt
import numpy as np
from .stackedbar import plot_stacked_bar
from utils import check_kwargs_list


def _parse_kwargs(data, **kwargs):
    kwargs_list = [
        {'key': 'ax', 'default': None, 'type': None},
        {'key': 'boxoff', 'default': True, 'type': bool},
        {'key': 'color', 'default': [None for _ in data], 'type': list},
        {'key': 'dpi', 'default': 100, 'type': float},
        {'key': 'edgecolor', 'default': ['#FFFFFF' for _ in data], 'type': tuple},
        {'key': 'figsize', 'default': (9, 3), 'type': tuple},
        {'key': 'linewidth', 'default': 0.3, 'type': float},
        {'key': 'num', 'default': None, 'type': str},
        {'key': 'title', 'default': 'Circadian Cycle', 'type': str},
        {'key': 'width', 'default': 1, 'type': float},
        {'key': 'xlabel', 'default': 'Hours', 'type': str},
        {'key': 'xlim', 'default': None, 'type': tuple},
        {'key': 'ylabel', 'default': 'Probability', 'type': str},
        {'key': 'ylim', 'default': [0, 1], 'type': tuple}
    ]
    kwargs = check_kwargs_list(kwargs_list, **kwargs)

    return kwargs


def plot_circadian_cycle(data, labels, **kwargs):
    kwargs = _parse_kwargs(data, **kwargs)

    if kwargs.get('ax') is None:
        plt.figure(num=kwargs.get('num'), figsize=kwargs.get(
            'figsize'), dpi=kwargs.get('dpi'))
        kwargs['ax'] = plt.gca()

    plot_stacked_bar(range(24), data, labels=labels, xticks=range(
        25), legend_anchor=(1.15, 1.1), align='edge', **kwargs)

    return
