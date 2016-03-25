from unittest import TestCase, skip

from snake.tasks import Task, TaskRegistry


class Flag(object):
    def __init__(self):
        self.value = False

    def __nonzero__(self):
        return self.value

    def set(self):
        self.value = True


class TaskTests(TestCase):
    def test_executing_runs_underlying_function(self):
        pass

    @skip('Not sure if this is necessary (yet)')
    def test_it_only_passes_kwargs_that_function_knows_about(self):
        pass


class TaskRegistryTests(TestCase):
    def setUp(self):
        super(TaskRegistryTests, self).setUp()
        self.registry = TaskRegistry()

    def test_function_can_be_called_normally_after_registration(self):
        called = Flag()

        @self.registry.add_task("Description")
        def flag():
            called.set()

        flag()
        self.assertTrue(called)

    def test_it_executes_task_by_label(self):
        called = Flag()

        @self.registry.add_task("Description")
        def flag():
            called.set()

        self.registry.execute('flag')
        self.assertTrue(called)

    def test_it_raises_key_error_for_unknown_label(self):
        with self.assertRaisesRegexp(KeyError, 'Unknown task: something'):
            self.registry.execute('something')

    def test_it_handles_namespacing_tasks(self):
        called = Flag()

        @self.registry.add_namespace
        def name():

            @self.registry.add_task("Description")
            def space():
                called.set()

        self.registry.execute('name:space')
        self.assertTrue(called)

    def test_it_handles_nested_namespacing(self):
        called = Flag()

        @self.registry.add_namespace
        def deeper():

            @self.registry.add_namespace
            def name():

                @self.registry.add_task("Description")
                def space():
                    called.set()

        self.registry.execute('deeper:name:space')
        self.assertTrue(called)
