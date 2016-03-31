from imp import load_source
from os import environ, path, getcwd
from six import print_
from sys import exit, stderr, argv, exc_info
from traceback import extract_tb

from .parser import ApplicationArgsParser as parser
from .shell import ShellWrapper
from .tasks import TaskRegistry, NoSuchTaskException
from .version import VERSION


class Application(object):
    def __init__(self):
        self.registry = TaskRegistry('snake')

    def info(self, message):
        """Logs a message to stdout"""
        print_(message)

    def error(self, message):
        """Logs a message to stderr"""
        print_(message, file=stderr)

    def run(self):
        tasks, args, opts = parser.parse(argv[1:])
        if opts.version:
            self.info('snake, version %s' % VERSION)
            return

        try:
            self._run(tasks, args, opts)
        except Exception as e:
            self._handle_exception(e, opts)

    def _run(self, tasks, args, opts):
        self._load_manifest(opts)

        if opts.show_tasks:
            self._list_tasks()
            return

        if tasks:
            for task in tasks:
                self._execute_task(task, args)
        else:
            # Run the default task
            self._execute_task(None, args)

    def _handle_exception(self, e, opts):
        self.error('snake aborted!')
        self.error(str(e))

        tb = extract_tb(exc_info()[2])
        self._print_stack_trace(tb, verbose=opts.trace)

        if not opts.trace:
            self.error('')  # TODO: Replace this with the task hierarchy
            self.error('(See full trace by running task with --trace)')

        exit(1)

    def _print_stack_trace(self, tb, verbose=False):
        for module, lineno, func, _ in reversed(tb):
            if not verbose and self._is_library_module(module):
                continue

            self.error("%s:%d:in `%s'" % (module, lineno, func))

    def _is_library_module(self, module):
        library_path = __file__[:__file__.rindex('/')]
        return module.startswith(library_path)

    def _load_manifest(self, opts):
        filename = opts.filename or 'Snakefile'
        if not path.isabs(filename):
            filename = path.join(getcwd(), filename)

        try:
            module = load_source('Snakefile', filename)
        except IOError as e:
            message = "No Snakefile found"
            if opts.filename:
                message += " (looking for: %s)" % opts.filename

            raise Exception(message)
        else:
            self._register_default_task(module)

    def _register_default_task(self, module):
        default_task = getattr(module, 'default', None)
        self.registry.default = default_task

    def _list_tasks(self):
        self.info(self.registry.view_all())

    def _execute_task(self, task, args):
        try:
            self.registry.execute(task, **args)
        except NoSuchTaskException as e:
            raise Exception("Don't know how to build task: %s" % e)


_instance = Application()
_runner = ShellWrapper(_instance)

env = environ
sh = _runner.execute
task = _instance.registry.add_task
namespace = _instance.registry.add_namespace
