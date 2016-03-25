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

    def _add_task(self, f, desc):
        label = ':'.join(self.__working_namespace + [f.__name__])
        self._tasks[label] = Task(f, desc)
