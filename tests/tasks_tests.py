from six import StringIO

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

        task = Task('flag', flag, "Test")

        task.execute()
        self.assertTrue(called)

    def test_it_can_accept_positional_and_keyword_args(self):
        args = {'a': 1}
        output = StringIO()

        def foo(a, b=2):
            output.write(str(a))
            output.write(str(b))

        task = Task('foo', foo, "Description")
        task.execute(**args)

        self.assertEqual('12', output.getvalue())

    def test_it_only_passes_kwargs_that_function_knows_about(self):
        args = {'a': 1, 'b': 2, 'c': 3}

        def foo(a, b):
            pass

        task = Task('foo', foo, "Description")
        task.execute(**args)

    def test_it_uses_friendly_error_message_when_missing_positional_args(self):
        args = {'a': 1}

        def bar(a, b):
            pass

        task = Task('foo:bar', bar, "Description")

        with self.assertRaisesRegexp(TypeError, r"^foo:bar requires argument\(s\): a, b$"):
            task.execute(**args)

    def test_it_bubbles_up_other_type_errors(self):
        def foo():
            1 + ''

        task = Task('foo', foo, "Description")

        with self.assertRaisesRegexp(TypeError, r"unsupported operand type"):
            task.execute()

    def test_required_args_returns_list_of_positional_args(self):
        def foo(a, b):
            pass

        task = Task('foo', foo, "Description")

        self.assertEqual(['a', 'b'], task.required_args())

    def test_required_args_returns_only_positional_args(self):
        def foo(a, b, c=1, d=2):
            pass

        task = Task('foo', foo, "Description")

        self.assertEqual(['a', 'b'], task.required_args())

    def test_required_args_ignores_splat_args(self):
        def foo(*args):
            pass

        task = Task('foo', foo, "Description")

        self.assertEqual([], task.required_args())

    def test_required_args_ignores_splat_kwargs(self):
        def foo(a, **kwargs):
            pass

        task = Task('foo', foo, "Description")

        self.assertEqual(['a'], task.required_args())

    def test_optional_args_returns_list_of_keyword_args(self):
        def foo(one=1, two=2):
            pass

        task = Task('foo', foo, "Description")

        self.assertEqual({'one': 1, 'two': 2}, task.optional_args())

    def test_optional_args_does_not_include_positional_args(self):
        def foo(one, two=2, three=3):
            pass

        task = Task('foo', foo, "Description")

        self.assertEqual({'two': 2, 'three': 3}, task.optional_args())

    def test_optional_args_does_not_include_splat_args(self):
        def foo(*args):
            pass

        task = Task('foo', foo, "Description")

        self.assertEqual({}, task.optional_args())

    def test_optional_args_does_not_include_splat_kwargs(self):
        def foo(one=1, **kwargs):
            pass

        task = Task('foo', foo, "Description")

        self.assertEqual({'one': 1}, task.optional_args())


class TaskRegistryTests(TestCase):
    def setUp(self):
        super(TaskRegistryTests, self).setUp()
        self.registry = TaskRegistry('snake')

    def test_function_can_be_called_normally_after_registration(self):
        called = Flag()

        @self.registry.add_task
        def flag():
            called.set()

        flag()
        self.assertTrue(called)

    def test_it_executes_task_by_label(self):
        called = Flag()

        @self.registry.add_task
        def foo():
            called.set()

        self.registry.execute('foo')
        self.assertTrue(called)

    def test_it_raises_for_unknown_label(self):
        with self.assertRaisesRegexp(NoSuchTaskException, r'something'):
            self.registry.execute('something')

    def test_it_runs_default_task_when_no_tasks_specified(self):
        called = Flag()

        @self.registry.add_task
        def foo():
            called.set()

        self.registry.default = 'foo'
        self.registry.execute(None)

    def test_it_raises_assertion_when_default_is_not_string(self):
        with self.assertRaisesRegexp(AssertionError, r"default task must be a string"):
            self.registry.default = lambda: True

    def test_it_raises_with_default_when_no_default(self):
        with self.assertRaisesRegexp(NoSuchTaskException, r'default'):
            self.registry.execute(None)

    def test_it_handles_namespacing_tasks(self):
        called = Flag()

        @self.registry.add_namespace
        def name():

            @self.registry.add_task
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

                @self.registry.add_task
                def space():
                    called.set()

        self.registry.execute('deeper:name:space')
        self.assertTrue(called)

    def test_it_executes_dependencies(self):
        one_called = Flag()
        two_called = Flag()

        @self.registry.add_task(requires=['two'])
        def one():
            one_called.set()

        @self.registry.add_task
        def two():
            two_called.set()

        self.registry.execute('one')
        self.assertTrue(two_called)
        self.assertTrue(one_called)

    def test_it_renders_nothing_when_no_tasks(self):
        table = self.registry.view_all()
        self.assertEqual('', table)

    def test_it_renders_tasks_in_table_form(self):

        @self.registry.add_task
        def build():
            """Builds"""

        @self.registry.add_task
        def compile():
            """Compiles"""

        expected = [
            'snake build    # Builds',
            'snake compile  # Compiles',
        ]

        self.assertEqual('\n'.join(expected), self.registry.view_all())

    def test_it_renders_tasks_with_arguments(self):

        @self.registry.add_task
        def build(medium='container'):
            """Builds"""

        @self.registry.add_task
        def compile(target, optimization='full'):
            """Compiles"""

        expected = [
            'snake build [medium=container]                     # Builds',
            'snake compile target={target} [optimization=full]  # Compiles',
        ]

        self.assertEqual('\n'.join(expected), self.registry.view_all())

    def test_it_stops_rendering_description_at_the_first_newline(self):

        @self.registry.add_task
        def descriptive():
            """
            This is a long description.

            What follows is blah blah blah.
            """

        expected = 'snake descriptive  # This is a long description.'

        self.assertEqual(expected, self.registry.view_all())

    def test_it_does_not_render_tasks_without_descriptions(self):

        @self.registry.add_task
        def something():
            pass

        self.assertEqual('', self.registry.view_all())
