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

def check_kwargs_list(kwargs_list, **kwargs):
    for kwarg in kwargs_list:
        kwargs[kwarg['key']] = kwargs.get(kwarg['key'], kwarg['default'])

        if kwarg['type'] is not None:
            if (kwargs.get(kwarg['key']) is None) and (kwarg['default'] is None):
                pass
            elif kwargs.get(kwarg['key']) is None:
                pass
            else:
                try:
                    if ((kwarg['type'] == list) or (kwarg['type'] == tuple)) and (type(kwargs.get(kwarg['key'])) is str):
                        kwargs[kwarg['key']] = [kwargs.get(kwarg['key'])]

                    kwargs[kwarg['key']] = kwarg['type'](kwargs.get(kwarg['key']))
                except:
                    raise TypeError("'" + kwarg['key'] + "' expected to be '" + kwarg['type'].__name__ + "', received '" + str(type(kwargs.get(kwarg['key'])).__name__) + "'")

    return kwargs
