import os


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


def get_filename(settings, sub: str, ses: str = None, run: str = None, suffix: str = None):
    filename = settings['general']['filename']

    if (type(sub) is list) and (len(sub) == 1):
        sub = sub[0]
    if (type(ses) is list) and (len(ses) == 1):
        ses = ses[0]
    if (type(run) is list) and (len(run) == 1):
        run = run[0]

    if (sub is not None) and (type(sub) is not str):
        raise TypeError('sub is of type ' + str(type(sub)) + ', but must be str.')
    if (ses is not None) and (type(ses) is not str):
        raise TypeError('ses is of type ' + str(type(ses)) + ', but must be str.')
    if (run is not None) and (type(run) is not str):
        raise TypeError('run is of type ' + str(type(run)) + ', but must be str.')

    if sub is None:
        raise ValueError('sub parameter cannot be None.')
    else:
        filename = filename.replace('<SUB>', sub)

    if (ses is None) or (ses == 'all') or (type(ses) is list):
        filename, _ = filename.split('_ses')
    elif (run is None) or (run == 'all') or (type(run) is list):
        filename, _ = filename.split('_run')
        filename = filename.replace('<SES>', ses)
    else:
        filename = filename.replace('<SES>', ses).replace('<RUN>', run)

    if suffix is not None:
        filename = filename + suffix

    return filename
