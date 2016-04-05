import re
from inspect import getargspec
from six import iteritems, iterkeys, itervalues, PY2

from .dependencies import DependencyGraph


class NoSuchTaskException(Exception):
    pass


class Task(object):
    """A task is the basic building block in a Snakefile manifest. Each task
    has an underlying function and a short description about what the task does.
    """
    def __init__(self, label, func, description):
        self.label = label
        self.func = func
        self.description = description

    def execute(self, **kwargs):
        """Executes the underlying function in the task.

        :param kwargs: the keyword arguments to pass to the function during
                       execution. Keywords that are not needed by the underlying
                       function will be ignored.
        """
        try:
            self.func(**self._sanitize_keyword_args(kwargs))
        except TypeError as e:
            if self._is_error_due_to_missing_arguments(e):
                args = ', '.join(self.required_args())
                raise TypeError("%s requires argument(s): %s" % (self.label, args))
            else:
                raise

    def required_args(self):
        """Returns the list of required arguments for the task.

        :return: list of required arg names as strings
        """
        positional_args, _ = self._positional_and_keyword_args()
        return positional_args

    def optional_args(self):
        """Returns the list of optional arguments for the task.

        :return: list of optional arg names as strings
        """
        _, keyword_args = self._positional_and_keyword_args()
        return keyword_args

    def _all_args(self):
        positional_args, keyword_args = self._positional_and_keyword_args()
        return positional_args + list(iterkeys(keyword_args))

    def _positional_and_keyword_args(self):
        args, _, _, defaults = getargspec(self.func)
        if not defaults:
            defaults = ()

        number_of_positional_args = len(args) - len(defaults)
        positional_args = args[:number_of_positional_args]

        keywords = args[number_of_positional_args:]
        keyword_args = dict(zip(keywords, defaults))

        return positional_args, keyword_args

    def _sanitize_keyword_args(self, kwargs):
        only_known_keywords = lambda kv: kv[0] in self._all_args()
        return dict(filter(only_known_keywords, iteritems(kwargs)))

    def _is_error_due_to_missing_arguments(self, e):
        # A bit of a hack, but we want to do this to make the error more specific
        # and easy to understand for the end user
        func = self.func.__name__

        # This error message seems to have been changed in Python 3.2
        if PY2:
            pattern = r'%s\(\) takes exactly \d{1,2} .*arguments? \(\d{1,2} given\)' % func
        else:
            pattern = r'%s\(\) missing \d{1,2} required positional argument:' % func

        return re.search(pattern, str(e))


class TaskRegistry(object):
    def __init__(self, name):
        self.name = name
        self.default = None

        self._tasks = {}
        self._dependencies = DependencyGraph()

        # Keeps a stack of namespace strings to handle nested namespaces.
        # The array is usually empty except when in the middle of evaluating
        # the contents of a namespace
        self.__working_namespace = []

    def __setattr__(self, name, value):
        if name == 'default':
            if value and not isinstance(value, str):
                raise AssertionError(
                    "The default task must be a string that "
                    "references the name of the task to run")

        super(TaskRegistry, self).__setattr__(name, value)

    def add_task(self, func=None, requires=None):
        """Defines a task by registering it. The function name is used as the task
        label and the function's docstring is used as the task description.

        :param func: the function to use as the task. Do not use this parameter
                     directly. It is only here to avoid having to use `@task`
                     with parenthesis when there are no other arguments to the
                     decorator.
        :param requires: a list of required tasks where each entry in the list is
                         a string task label
        :return: the function unmodified
        """
        if func:
            self._add_task(func, [])
            return func

        else:
            def wrapper(f):
                self._add_task(f, requires or [])
                return f

            return wrapper

    def add_namespace(self, f):
        """Defines a namespace for tasks. The name of the namespace will be the
        name of the function. This is useful for semantically grouping tasks
        together. Note that a function defined as a namespace will be executed
        on load in order to register all nested tasks.

        Namespaces are denoted with the `:' separator in task labels.

        :param f: the function to use as a namespace
        :return: the function unmodified
        """
        self.__working_namespace.append(f.__name__)
        f()
        self.__working_namespace.pop()
        return f

    def execute(self, _label, **kwargs):
        """Executes a number of tasks in order. The tasks are referenced by
        their names. Executes the default task if no tasks are supplied.

        :param tasks: list of task labels
        :param kwargs: the keyword arguments to pass to each task
        """
        if not _label:
            if not self.default:
                raise NoSuchTaskException('default')

            _label = self.default

        for dependency in self._dependencies.resolve(_label):
            self._execute_task(dependency, **kwargs)

    def view_all(self):
        """Formats the tasks using each task's label and description.

        :return: string formatted as a table of tasks
        """
        tasks = [task for task in itervalues(self._tasks)]
        return TaskListFormatter(tasks).tableize(self.name)

    def _execute_task(self, _label, **kwargs):
        try:
            task = self._tasks[_label]
        except KeyError:
            raise NoSuchTaskException(_label)

        task.execute(**kwargs)

    def _add_task(self, f, deps):
        label = ':'.join(self.__working_namespace + [f.__name__])

        description = f.__doc__
        if description:
            # Trim leading whitespace and only get the first line of the function doc
            description = description.lstrip().split('\n')[0]

        self._dependencies.add(label, deps)
        self._tasks[label] = Task(label, f, description)


class TaskListFormatter(object):
    def __init__(self, tasks):
        self._tasks = tasks

    def tableize(self, prefix):
        documented_tasks = [(self._task_signature(t), t.description)
                            for t in self._tasks if t.description]

        if not documented_tasks:
            return ''

        by_signature_length = lambda task: len(task[0])
        task_with_longest_signature = max(documented_tasks, key=by_signature_length)
        width = len(task_with_longest_signature[0])

        by_signature = lambda task: task[0]
        sorted_tasks = sorted(documented_tasks, key=by_signature)

        return '\n'.join('%s %s  # %s' %
                         (prefix, signature.ljust(width), description)
                         for signature, description in sorted_tasks)

    def _task_signature(self, task):
        """A task signature is the combination of the task name and its arguments"""
        return '%s%s' % (task.label, self._render_arg_list(task))

    def _render_arg_list(self, task):
        required_args = task.required_args()
        optional_args = task.optional_args()

        # Prefix the arg list with an empty space so that when the components are joined,
        # it will be padding if there are arguments or nothing if there aren't
        parts = ['']

        if required_args:
            parts.append(' '.join(self._format_required_arg(arg)
                                  for arg in required_args))

        if optional_args:
            parts.append(' '.join(self._format_optional_arg(arg)
                                  for arg in iteritems(optional_args)))

        return ' '.join(parts)

    def _format_required_arg(self, arg):
        return '%s={%s}' % (arg, arg)

    def _format_optional_arg(self, arg):
        name, default = arg
        return '[%s=%s]' % (name, default)
