class Task(object):
    def __init__(self, func, description):
        self.func = func
        self.description = description

    def execute(self, **kwargs):
        self.func(**kwargs)


class TaskRegistry(object):
    def __init__(self):
        self._tasks = {}

        # Keeps a stack of namespace strings to handle nest namespaces.
        # The array is usually empty except when in the middle of evaluating
        # the contents of a namespace
        self.__working_namespace = []

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

    def execute(self, label, **kwargs):
        try:
            task = self._tasks[label]
        except KeyError:
            raise KeyError('Unknown task: %s' % label)

        task.execute(**kwargs)

    def view_all(self):
        print self._tasks
        tasks = [(label, t.description) for label, t in self._tasks.iteritems()]
        return TaskListFormatter(tasks).tableize(padding=4)

    def _add_task(self, f, desc):
        label = ':'.join(self.__working_namespace + [f.__name__])
        self._tasks[label] = Task(f, desc)


class TaskListFormatter(object):
    def __init__(self, tasks):
        print tasks
        self._tasks = tasks

    def tableize(self, padding=0):
        by_length = lambda (label, _): len(label)

        try:
            longest_task_label, _ = max(self._tasks, key=by_length)
        except ValueError:
            return ''

        width = len(longest_task_label) + padding
        return '\n'.join('%s  # %s' % (label.ljust(width), desc) for label, desc in self._tasks)
