import matplotlib.pyplot as plt
from utils import check_kwargs_list


def _parse_kwargs(**kwargs):
    kwargs_list = [
        {'key': 'ax', 'default': None, 'type': None},
        {'key': 'boxoff', 'default': True, 'type': bool},
        {'key': 'color', 'default': '#1f77b4', 'type': str},
        {'key': 'dpi', 'default': 100, 'type': float},
        {'key': 'figsize', 'default': (6, 3), 'type': tuple},
        {'key': 'linewidth', 'default': 0.25, 'type': float},
        {'key': 'num', 'default': None, 'type': str},
        {'key': 'title', 'default': 'Circadian Cycle', 'type': str},
        {'key': 'xlabel', 'default': 'Hours', 'type': str},
        {'key': 'xlim', 'default': None, 'type': tuple},
        {'key': 'ylabel', 'default': 'Probability', 'type': str},
        {'key': 'ylim', 'default': [0, 1], 'type': tuple}
    ]
    kwargs = check_kwargs_list(kwargs_list, **kwargs)

    return kwargs

def plot_circadian_cycle(data, **kwargs):
    kwargs = _parse_kwargs(**kwargs)

    if kwargs.get('ax') is None:
        plt.figure(num=kwargs.get('num'), figsize=kwargs.get('figsize'), dpi=kwargs.get('dpi'))
        ax = plt.gca()
    else:
        ax = kwargs.get('ax')
    
    ax.bar(range(24), data, color=kwargs.get('color'), edgecolor=kwargs.get('color'))

    ax.set_title(kwargs.get('title'))
    ax.set_xlabel(kwargs.get('xlabel'))
    ax.set_ylabel(kwargs.get('ylabel'))

    ax.set_xticks(range(24))

    ax.set_xlim(kwargs.get('xlim'))
    ax.set_ylim(kwargs.get('ylim'))

    if kwargs.get('boxoff') is True:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    return