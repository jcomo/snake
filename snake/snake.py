from __future__ import print_function

from imp import load_source
from os import environ
from sys import exit, stderr, argv

from .tasks import TaskRegistry
from .shell import ShellWrapper


class Snake(object):
    def __init__(self):
        self.registry = TaskRegistry()

    def run(self):
        self._load_manifest()
        self._execute_command()

    def abort(self, code):
        exit(code)

    def info(self, message):
        print(message)

    def error(self, message):
        print(message, file=stderr)

    def _load_manifest(self):
        try:
            load_source('Snakefile', './Snakefile')
        except IOError as e:
            self.error("No Snakefile found")
            self.abort(1)

    def _execute_command(self):
        try:
            subcommand = argv[1]
        except IndexError:
            subcommand = 'default'

        # TODO: make a parser for args, kwargs, etc
        if subcommand == '-T':
            self.info(self.registry.view_all())
            return

        try:
            self.registry.execute(subcommand)
        except KeyError:
            self.error("Don't know how to build task: %s" % subcommand)
            self.abort(1)


_instance = Snake()
_runner = ShellWrapper(_instance)

env = environ
sh = _runner.execute
task = _instance.registry.add_task
namespace = _instance.registry.add_namespace
