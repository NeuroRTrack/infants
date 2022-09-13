import os

def create_output_dir(settings):
    output_dir = settings['output_dir']
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=False)

    output_dir = os.path.join(output_dir, 'sub-' + settings['sub'])
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=False)

    output_dir = os.path.join(output_dir, 'ses-' + settings['ses'])
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=False)

    return output_dir
