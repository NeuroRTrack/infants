import os


def check_all_setting(var, sep: str, suffix: str, path: str):
    if (var == 'all') or (var == ['all']):
        var = []
        for file in os.listdir(path):
            if file.endswith(suffix):
                _, _var = file.split(sep)
                _var = _var.split('_')[0]
                _var = _var.replace('-', '')
                var.append(_var)

    if type(var) is str:
        var = [var]

    var.sort()

    return var
