from __future__ import print_function  # TODO: use logging
import subprocess
import sys
import imp

from .tasks import TaskRegistry


def sh(command):
    _instance.info(command)
    exit_status = subprocess.call(command, shell=True)
    if exit_status != 0:
        # TODO: rake-style aborting
        _instance.abort(exit_status)


class Snake(object):
    def __init__(self):
        self.registry = TaskRegistry()

    def run(self):
        self._load_manifest()
        self._execute_command()

    def abort(self, code):
        sys.exit(code)

    def info(self, message):
        print(message)

    def error(self, message):
        print(message, file=sys.stderr)

    def _load_manifest(self):
        try:
            imp.load_source('Snakefile', './Snakefile')
        except IOError as e:
            self.error("No Snakefile found")
            self.abort(1)

    def _execute_command(self):
        try:
            subcommand = sys.argv[1]
        except IndexError:
            subcommand = 'default'

        try:
            self.registry.execute(subcommand)
        except KeyError:
            self.error("Don't know how to build task: %s" % subcommand)
            self.abort(1)


_instance = Snake()

task = _instance.registry.add_task
namespace = _instance.registry.add_namespace
