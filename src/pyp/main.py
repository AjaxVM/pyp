
import argparse
import subprocess
import sys

from .commands import Commands
from .errors import UserError
from .project_def import ProjectDef


class Controller:

    def __init__(self):
        self.project = ProjectDef(self)

    #     self.cmds = {}
        self.cmd_def = argparse.ArgumentParser(
            description='Pyp project management tools (0.0.1)',
            prog='pyp'
        )
        self._set_root_commands()
        self.subcommands = self.cmd_def.add_subparsers(dest='_cmd_name', help='command to execute')

        self.env = None # None uses default
        self.run_global = False
        
        self.commands = Commands(self)

    def _set_root_commands(self):
        self.cmd_def.add_argument('-v', '--version', action='version', version='0.0.1')
        self.cmd_def.add_argument('-e', '--env', default=None, help='which virtual env to start, defined in package config file')
        self.cmd_def.add_argument('-g', '--global', default=False, dest='run_global', action='store_true', help='set tool to global mode, so no venv will be used to execute commands')

    def run(self, args):
        # make sure we see help if no args are sent
        args = args or sys.argv[1::]
        if len(args) == 0:
            args.append('-h')

        opt = self.cmd_def.parse_args(args)

        if opt.env and opt.run_global:
            print('Can not use -e and -g together')
            return

        self.env = opt.env
        self.run_global = opt.run_global

        print('env: ', self.env, 'run_global: ', self.run_global)

        if opt._cmd_name:
            # self._run_command(opt)
            self.commands.run(opt._cmd_name, opt)


def run(args=None):
    ctrl = Controller()

    ctrl.run(args)
