from StringIO import StringIO

from unittest2 import TestCase

from snake.tasks import Task, TaskRegistry, NoSuchTaskException


class Flag(object):
    def __init__(self):
        self.value = False

    def __nonzero__(self):
        return self.value

    def set(self):
        self.value = True


class TaskTests(TestCase):
    def test_executing_runs_underlying_function(self):
        called = Flag()

        def flag():
            called.set()

        task = Task(flag, "Test")

        task.execute()
        self.assertTrue(called)

    def test_it_can_accept_positional_and_keyword_args(self):
        args = {'a': 1}
        output = StringIO()

        def foo(a, b=2):
            output.write(a)
            output.write(b)

        task = Task(foo, "Description")
        task.execute(**args)

        self.assertEqual('12', output.getvalue())

    def test_it_only_passes_kwargs_that_function_knows_about(self):
        args = {'a': 1, 'b': 2, 'c': 3}

        def foo(a, b):
            pass

        task = Task(foo, "Description")
        task.execute(**args)


class TaskRegistryTests(TestCase):
    def setUp(self):
        super(TaskRegistryTests, self).setUp()
        self.registry = TaskRegistry('snake')

    def test_function_can_be_called_normally_after_registration(self):
        called = Flag()

        @self.registry.add_task("Description")
        def flag():
            called.set()

        flag()
        self.assertTrue(called)

    def test_it_executes_task_by_label(self):
        one_called = Flag()
        two_called = Flag()

        @self.registry.add_task("Description")
        def one():
            one_called.set()

        @self.registry.add_task("Description")
        def two():
            two_called.set()

        self.registry.execute(['one', 'two'])
        self.assertTrue(one_called)
        self.assertTrue(two_called)

    def test_it_raises_for_unknown_label(self):
        with self.assertRaisesRegexp(NoSuchTaskException, r'something'):
            self.registry.execute(['something'])

    def test_it_runs_default_task_when_no_tasks_specified(self):
        called = Flag()

        @self.registry.add_task("Test")
        def foo():
            called.set()

        self.registry.default = 'foo'
        self.registry.execute([])

    def test_it_raises_assertion_when_default_is_not_string(self):
        with self.assertRaisesRegexp(AssertionError, r"default task must be a string"):
            self.registry.default = lambda: True

    def test_it_raises_with_default_when_no_default(self):
        with self.assertRaisesRegexp(NoSuchTaskException, r'default'):
            self.registry.execute([])

    def test_it_handles_namespacing_tasks(self):
        called = Flag()

        @self.registry.add_namespace
        def name():

            @self.registry.add_task("Description")
            def space():
                called.set()

        self.registry.execute(['name:space'])
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

        self.registry.execute(['deeper:name:space'])
        self.assertTrue(called)

    def test_it_renders_tasks_in_table_form(self):

        @self.registry.add_task("Builds")
        def build():
            pass

        @self.registry.add_task("Compiles")
        def compile():
            pass

        expected = [
            'snake build    # Builds',
            'snake compile  # Compiles',
        ]

        self.assertEqual('\n'.join(expected), self.registry.view_all())

    def test_it_renders_nothing_when_no_tasks(self):
        table = self.registry.view_all()
        self.assertEqual('', table)
