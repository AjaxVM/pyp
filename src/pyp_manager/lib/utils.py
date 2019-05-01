
import os

def config_path(config_file):
    path = os.path.dirname(os.path.abspath(__file__))
    head, tail = os.path.split(path)

    if tail == 'lib':
        path = head

    return os.path.join(path, 'config', config_file)
