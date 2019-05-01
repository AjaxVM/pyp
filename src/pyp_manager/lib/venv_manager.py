
import os
import shutil
import subprocess
import venv

from .errors import UserError
from .project_def import PYP_DEFAULT_VENV, PYP_VENV_DIR

class VenvManager:
    def __init__(self, ctrl):
        self.ctrl = ctrl

        self.target = None # which venv we are targeting - None maps to "default"
        self.run_global = False

    def create(self, name=None, force=False):
        venv_path = os.path.join(PYP_VENV_DIR, name or PYP_DEFAULT_VENV)
        if os.path.isdir(venv_path):
            if force:
                shutil.rmtree(venv_path)
            elif name:
                raise UserError(f'venv "{name}" already exists - overwrite with --force')
            else:
                raise UserError('default venv already exists - overwrite with --force')
        # todo - do we want symlinks?
        builder = venv.EnvBuilder(symlinks=True, with_pip=True)
        builder.create(venv_path)

    def get_env(self):
        if self.run_global:
            return os.environ
        env = os.environ.copy()

        # todo: look at this closer than the 5 minutes I spent on it to make sure this works as expected/recommended
        if 'PYTHONHOME' in env:
            del env['PYTHONHOME']
        if 'PYTHONPATH' in env:
            del env['PYTHONPATH']

        venv_path = os.path.join(PYP_VENV_DIR, self.target or PYP_DEFAULT_VENV)
        env['PATH'] = os.pathsep.join([venv_path, env['PATH']])

        return env

    # def is_dirty(self

    def execute(self, args, pipe=False):
        if pipe:
            return subprocess.Popen(args, env=self.get_env(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return subprocess.call(args, env=self.get_env())

    def install(self, packages):
        self.execute(['pip', 'install', *packages])
