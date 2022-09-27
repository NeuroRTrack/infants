import os


def check_all_setting(var, sep: str, path: str, prefix: str = None, suffix: str = None):
    if (prefix is None) and (suffix is None):
        raise ValueError(
            'prefix and suffix parameters cannot be None at the same time.')

    if (var == 'all') or (var == ['all']):
        var = []
        for file in os.listdir(path):
            prefix_none = (prefix is None) and (file.endswith(suffix))
            suffix_none = (suffix is None) and (file.startswith(prefix))
            prefix_suffix = ((prefix is not None) and (file.startswith(prefix))) and ((suffix is not None) and (file.endswith(suffix)))

            if  prefix_none or suffix_none or prefix_suffix:
                _, _var = file.split(sep)
                _var = _var.split('_')[0]
                _var = _var.replace('-', '')
                var.append(_var)

    if type(var) is str:
        var = [var]

    var.sort()

    return var
