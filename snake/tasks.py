import re
from inspect import getargspec
from six import iteritems


class NoSuchTaskException(Exception):
    pass


class Task(object):
    """A task is the basic building block in a Snakefile manifest. Each task
    has an underlying function and a short description about what the task does.
    """
    def __init__(self, func, description):
        self.label = func.__name__  # TODO: use this instead of of the tuples
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
                raise TypeError("%s requires arguments: %s" % (self.label, args))
            else:
                raise

    def required_args(self):
        """Returns the list of required arguments for the task.

        :return: list of required arg names as strings
        """
        args, _, _, defaults = getargspec(self.func)
        if not defaults:
            defaults = ()

        number_of_positional_args = len(args) - len(defaults)
        return args[:number_of_positional_args]

    def _sanitize_keyword_args(self, kwargs):
        only_known_keywords = lambda kv: kv[0] in self._func_args()
        return dict(filter(only_known_keywords, iteritems(kwargs)))

    def _func_args(self):
        args, _, _, _ = getargspec(self.func)
        return args

    def _is_error_due_to_missing_arguments(self, e):
        # A bit of a hack, but we want to do this to make the error more specific
        # and easy to understand for the end user
        missing_args_pattern = r'%s\(\) takes exactly \d{1,2} arguments \(\d{1,2} given\)' % self.func.__name__
        return re.search(missing_args_pattern, str(e))


class TaskRegistry(object):
    def __init__(self, name):
        self.name = name
        self.default = None
        self._tasks = {}

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

    def add_task(self, description):
        """Defines a task by registering it. The function name is used as the task
        label.

        :param description: a brief explanation of what the task does. Used when
                            listing tasks.
        :return: the function unmodified
        """
        def wrapper(f):
            self._add_task(f, description)
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

    def execute(self, tasks, **kwargs):
        """Executes a number of tasks in order. The tasks are referenced by
        their names. Executes the default task if no tasks are supplied.

        :param tasks: list of task labels
        :param kwargs: the keyword arguments to pass to each task
        """
        if not tasks:
            self._execute_task(self.default, 'default', **kwargs)
        else:
            for label in tasks:
                self._execute_task(label, label, **kwargs)

    def view_all(self):
        """Formats the tasks using each task's label and description.

        :return: string formatted as a table of tasks
        """
        tasks = [(label, t.description) for label, t in iteritems(self._tasks)]
        return TaskListFormatter(tasks).tableize(self.name)

    def _execute_task(self, label, friendly, **kwargs):
        try:
            task = self._tasks[label]
        except KeyError:
            raise NoSuchTaskException(friendly)

        task.execute(**kwargs)

    def _add_task(self, f, desc):
        label = ':'.join(self.__working_namespace + [f.__name__])
        self._tasks[label] = Task(f, desc)


class TaskListFormatter(object):
    def __init__(self, tasks):
        """Formats tasks in various ways.

        :param tasks: list of task info pairs of (label, description)
        """
        self._tasks = tasks

    def tableize(self, prefix):
        by_label = lambda task: task[0]
        by_label_length = lambda task: len(task[0])

        try:
            longest_task_label, _ = max(self._tasks, key=by_label_length)
        except ValueError:
            return ''

        width = len(longest_task_label)
        sorted_tasks = sorted(self._tasks, key=by_label)

        return '\n'.join('%s %s  # %s' % (prefix, label.ljust(width), desc)
                         for label, desc in sorted_tasks)
