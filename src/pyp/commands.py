
import argparse

from .errors import UserError

class Commands:
    def __init__(self, ctrl):
        self.ctrl = ctrl
        self._build_commands()

    def _build_commands(self):
        sub = self.ctrl.subcommands

        # command: setup
        arg_def = sub.add_parser('setup')
        arg_def.add_argument('-f', '--force', action='store_true', help='force setup to rerun, overwriting any existing project definition')

        # command: install
        arg_def = sub.add_parser('install')
        arg_def.add_argument('-t', '--test', action='store_true', help='install for testing')
        arg_def.add_argument('packages', action='append', help='install N packages')

        # command: install_locked
        arg_def = sub.add_parser('install_locked')
        arg_def.add_argument('-t', '--test', action='store_true', help='install for testing')

    def run(self, cmd, opt):
        try:
            getattr(self, f'run_{cmd}')(opt)
        except UserError as e:
            print(f'{cmd}: {e}')

    #### actual commands

    def run_setup(self, opt):
        self.ctrl.project.setup(opt.force)

    def run_install(self, opt):
        self.ctrl.project.install(opt.test, opt.packages)

    def run_install_locked(self, opt):
        self.ctrl.project.install_locked(opt.test)
