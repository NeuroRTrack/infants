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
