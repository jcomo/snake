from __future__ import print_function  # TODO: use logging
import subprocess
import sys
import imp


def sh(command):
    _instance.info(command)
    exit_status = subprocess.call(command, shell=True)
    if exit_status != 0:
        # TODO: rake-style aborting
        _instance.abort(exit_status)


# FIXME: function wrapping?
def task(desc):
    def _task(f):
        _instance.add_task(f, desc)

        def __task(*args, **kwargs):
            return f(*args, **kwargs)
        return __task
    return _task


class Snake(object):
    def __init__(self):
        self._tasks = {}

    def add_task(self, f, desc):
        # TODO: task class
        self._tasks[f.__name__] = (f, desc)

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
            f, _ = self._tasks[subcommand]
        except KeyError:
            self.error("Don't know how to build task: %s" % subcommand)
            self.abort(1)
        else:
            # TODO: argument passing
            f()


_instance = Snake()
