from __future__ import print_function

from imp import load_source
from os import environ
from sys import exit, stderr, argv

from .parser import CommandLineParser as parser
from .shell import ShellWrapper
from .tasks import TaskRegistry


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
            module = load_source('Snakefile', './Snakefile')
        except IOError as e:
            self.error("No Snakefile found")
            self.abort(1)
        else:
            self._register_default_task(module)

    def _register_default_task(self, module):
        default_task = getattr(module, 'default', None)
        self.registry.default = default_task

    def _execute_command(self):
        tasks, args, flags = parser.parse(argv[1:])

        if 'T' in flags:
            self.info(self.registry.view_all())
            return

        try:
            self.registry.execute(tasks, **args)
        except KeyError as e:
            self.error("Don't know how to build task: %s" % e.message)
            self.abort(1)


_instance = Snake()
_runner = ShellWrapper(_instance)

env = environ
sh = _runner.execute
task = _instance.registry.add_task
namespace = _instance.registry.add_namespace
