
import hashlib
import json
import os
import subprocess
import venv

from .errors import UserError

PYP_FILE = 'pyp.json'

# todo: just use pyp.json

PYP_DIR = '.pyp'

PYP_DIRTY_FILE = os.path.join('.pyp', 'dirty_hash')

PYP_VENV = os.path.join('.pyp', 'venv')

PYP_TEST_VENV = os.path.join('.pyp', 'test_venv')

DEFAULT_PROJECT_CONFIG = {
    'name': os.path.split(os.getcwd())[-1],
    'description': '',
    'version': '0.0.1',
    'license': None,
    'requirements': [], # TODO: make a dict of name:version
    'scripts': {
        'start': 'python src/main.py',
        'test': '[test] python -m unittest discover'
    },
    'test_requirements': []
}

DEFAULT_PROJECT_SRC_TREE = {
    'dirs': ['src', 'test'],
    'files': ['src/main.py', 'test/__init__.py']
}

PYP_LOCK = 'pyp.lock.json'

class ProjectDef:
    def __init__(self, ctrl):
        self.ctrl = ctrl

        self.definition = None

    # interface

    def ensure_pyp_file(self):
        if not os.path.isfile(PYP_FILE):
            raise UserError('pyp.json missing, please create one or execute "pyp setup"')

    def write_config(self, data):
        self.ensure_pyp_file()
        data['requirements'] = sorted(data['requirements'])
        data['test_requirements'] = sorted(data['test_requirements'])

        with open(PYP_FILE, 'w') as output:
            output.write(json.dumps(data, indent=2))

    def write_lock(self):
        # make sure we have both venvs ready
        self.ensure_venv()
        self.ensure_venv(True)

        env = self.get_env()
        test_env = self.get_env(True)

        pipe = subprocess.Popen(['pip', 'freeze'], env=env, stdout=subprocess.PIPE)
        reqs = pipe.communicate()[0].decode('utf-8').splitlines()

        pipe = subprocess.Popen(['pip', 'freeze'], env=test_env, stdout=subprocess.PIPE)
        treqs = pipe.communicate()[0].decode('utf-8').splitlines()

        with open(PYP_LOCK, 'w') as f:
            f.write(
                json.dumps({
                    'requirements': reqs,
                    'test_requirements': treqs
                }, indent=2)
            )

    def get_lock(self):
        if not os.path.isfile(PYP_LOCK):
            raise UserError(f'No pyp lock found, make sure you commit the created "{PYP_LOCK}". Otherwise, use "pyp install" to generate one')
        with open(PYP_LOCK, 'r') as f:
            return json.loads(f.read())

    def update_config(self):
        self.ensure_loaded()
        self.write_config(self.definition)

    def setup(self, force=False):
        if os.path.isfile(PYP_FILE):
            if force:
                os.unlink(PYP_FILE)
            else:
                raise UserError('pyp.json already exists - overwrite with --force')

        # get user input
        pname = input(f'Project Name ({DEFAULT_PROJECT_CONFIG["name"]}): ')
        pdesc = input('Description: ')
        pver = input('Version (0.0.1): ')
        src_tree = input('Create default src tree [yes,no] (yes): ') or 'yes'

        project_config = DEFAULT_PROJECT_CONFIG.copy()

        project_config['name'] = pname or DEFAULT_PROJECT_CONFIG['name']
        project_config['description'] = pdesc or DEFAULT_PROJECT_CONFIG['description']
        project_config['version'] = pver or DEFAULT_PROJECT_CONFIG['version']

        self.write_config(project_config)

        if src_tree.lower() in ('yes', 'y'):
            for d in DEFAULT_PROJECT_SRC_TREE['dirs']:
                if not os.path.isdir(d):
                    os.mkdir(d)
            for f in DEFAULT_PROJECT_SRC_TREE['files']:
                if not os.path.isfile(f):
                    open(f, 'a').close()

    def load_config(self):
        self.ensure_pyp_file()

        try:
            with open(PYP_FILE, 'r') as _file:
                # TODO: consider json5 (using pyjson5 for speed)
                proj_data = json.loads(_file.read())
        except:
            raise UserError('Invalid project configuration file, could not parse JSON contents')

        for key in DEFAULT_PROJECT_CONFIG:
            # ensure we have all of the proper information
            if not key in proj_data:
                raise UserError(f'Invalid project configuration file, missing key "{key}"')

        self.definition = proj_data

    def ensure_loaded(self):
        if not self.definition:
            self.load_config()

    def have_pyp_dir(self):
        return os.path.isdir(PYP_DIR)

    def ensure_pyp_dir(self):
        if not os.path.isdir(PYP_DIR):
            os.path.mkdir(PYP_DIR)

    def is_dirty(self):
        self.ensure_pyp_file()

        if not self.have_pyp_dir():
            return True
        if not os.path.isfile(PYP_DIRTY_FILE):
            return True

        hasher = hashlib.md5()
        with open(PYP_FILE, 'rb') as f:
            hasher.update(f.read().strip())
        inhash = hasher.hexdigest()

        with open(PYP_DIRTY_FILE, 'rb') as f:
            outhash = f.read().strip()

        return inhash != outhash

    def update_dirty(self):
        self.ensure_pyp_file()
        
        self.ensure_pyp_dir()

        hasher = hashlib.md5()
        with open(PYP_FILE, 'rb') as f:
            hasher.update(f.read().strip())
        data = hasher.hexdigest()

        with open(PYP_DIRTY_FILE, 'wb') as f:
            f.write(data)

    def get_env(self, test=False):
        env = os.environ.copy()

        # todo: look at this closer than the 5 minutes I spent on it to make sure this works as expected/recommended
        env['PATH'] = f'{PYP_TEST_VENV if test else PYP_VENV}{os.pathsep}{env["PATH"]}'
        if 'PYTHONHOME' in env:
            del env['PYTHONHOME']
        if 'PYTHONPATH' in env:
            del env['PYTHONPATH']

        return env

    def install(self, test=False, packages=None):
        self.ensure_loaded()
        self.ensure_venv(test)
        env = self.get_env(test)
        if not packages:
            # install all the ones declared in our conf
            reqs = self.definition['requirements']
            if test:
                # we need both for test, d'oh
                reqs = reqs + self.definition['test_requirements']
            subprocess.call(['pip', 'install'] + reqs, env=env)
        else:
            code = subprocess.call(['pip', 'install', *packages], env=env)
            if code == 0:
                # everything installed, let's add to our definition
                reqs = self.definition['test_requirements'] if test else self.definition['requirements']
                reqs.extend(packages)
                self.update_config()
            else:
                raise Exception(f'Installation failed with code {code}')
        self.write_lock()

    def install_locked(self, test=False):
        lock = self.get_lock()
        reqs = lock['test_requirements'] if test else lock['requirements']

        self.ensure_venv(test)
        env = self.get_env(test)

        subprocess.call(['pip', 'install', *reqs], env=env)

    def ensure_venv(self, test=False):
        venv_path = PYP_TEST_VENV if test else PYP_VENV
        if not os.path.isdir(venv_path):
            # todo - do we want symlinks?
            builder = venv.EnvBuilder(symlinks=True, with_pip=True)
            builder.create(venv_path)


