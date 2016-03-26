from inspect import getargspec


class NoSuchTaskException(Exception):
    pass


class Task(object):
    def __init__(self, func, description):
        self.func = func
        self.description = description

    def execute(self, **kwargs):
        self.func(**self._sanitize_keyword_args(kwargs))

    def _sanitize_keyword_args(self, kwargs):
        only_known_keywords = lambda (k, _): k in self._func_args()
        return dict(filter(only_known_keywords, kwargs.iteritems()))

    def _func_args(self):
        args, _, _, _ = getargspec(self.func)
        return args


class TaskRegistry(object):
    def __init__(self):
        self.default = None
        self._tasks = {}

        # Keeps a stack of namespace strings to handle nest namespaces.
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
        def wrapper(f):
            self._add_task(f, description)
            return f
        return wrapper

    def add_namespace(self, f):
        self.__working_namespace.append(f.__name__)
        f()
        self.__working_namespace.pop()
        return f

    def execute(self, tasks, **kwargs):
        if not tasks:
            self._execute_task(self.default, 'default', **kwargs)
        else:
            for label in tasks:
                self._execute_task(label, label, **kwargs)

    def view_all(self):
        tasks = [(label, t.description) for label, t in self._tasks.iteritems()]
        return TaskListFormatter(tasks).tableize(padding=4)

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
        self._tasks = tasks

    def tableize(self, padding=0):
        by_label = lambda (label, _): label
        by_length = lambda (label, _): len(label)

        try:
            longest_task_label, _ = max(self._tasks, key=by_length)
        except ValueError:
            return ''

        width = len(longest_task_label) + padding
        sorted_tasks = sorted(self._tasks, key=by_label)

        return '\n'.join('%s  # %s' % (label.ljust(width), desc) for label, desc in sorted_tasks)
