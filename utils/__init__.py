import os
import warnings


class IgnoreWarnings(object):
    def __init__(self, message):
        self.message = message
    
    def __enter__(self):
        warnings.filterwarnings("ignore", message=f".*{self.message}.*")
    
    def __exit__(self, *_):
        warnings.filterwarnings("default", message=f".*{self.message}.*")


def create_output_dir(output_dir, sub, ses):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=False)

    output_dir = os.path.join(output_dir, 'sub-' + sub)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=False)

    output_dir = os.path.join(output_dir, 'ses-' + ses)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=False)

    return output_dir


def get_filename(settings, ses=None, run=None, suffix=None):
    filename = settings['general']['filename'].replace(
        '<SUB>', settings['general']['sub'])

    if ses is None: ses = settings['general']['ses']
    if run is None: run = settings['general']['run']

    if (type(ses) is list) and (len(ses) == 1): ses = ses[0]
    if (type(run) is list) and (len(run) == 1): run = run[0]

    if (ses == 'all') or (ses == ['all']) or (type(ses) is list):
            filename, _ = filename.split('_ses')
    else:
        filename = filename.replace('<SES>', ses)

        if (run == 'all') or (run == ['all']) or (type(run) is list):
            filename, _ = filename.split('_run')
        else:
            filename = filename.replace('<RUN>', run)

    if suffix is not None: filename = filename + suffix

    return filename


def check_all_setting(var, sep:str, suffix: str, path: str):
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