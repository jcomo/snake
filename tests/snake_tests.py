from tests.utils import IntegrationTest


class SnakeTests(IntegrationTest):
    def test_it_exits_with_error_when_no_snakefile_found(self):
        result = self.execute('snake')

        self.assertStdoutEmpty(result)
        self.assertStderrMatches(result, r'^snake aborted!$')
        self.assertStderrMatches(result, r'^No Snakefile found$')
        self.assertStatusEqual(result, 1)

    def test_it_exits_with_error_when_task_name_not_found(self):
        self.use_snakefile("""
            from snake import *

            @task
            def something():
                '''Do something'''
        """)

        result = self.execute('snake blah')

        self.assertStdoutEmpty(result)
        self.assertStderrMatches(result, "Don't know how to build task: blah")
        self.assertStatusEqual(result, 1)

    def test_it_runs_default_task_when_none_specified(self):
        self.use_snakefile("""
            from __future__ import print_function
            from snake import *

            default = 'greet'

            @task
            def greet():
                print('hi')
        """)

        result = self.execute('snake')

        self.assertStderrEmpty(result)
        self.assertStdoutEqual(result, ['hi'])
        self.assertStatusEqual(result, 0)

    def test_it_outputs_command_when_running_shell(self):
        self.use_snakefile("""
            from snake import *

            @task
            def test():
                sh('true')
        """)

        result = self.execute('snake test')

        self.assertStderrEmpty(result)
        self.assertStdoutEqual(result, ['true'])
        self.assertStatusEqual(result, 0)

    def test_it_passes_arguments_to_tasks(self):
        self.use_snakefile("""
            from __future__ import print_function
            from snake import *

            @task
            def hello(name='World'):
                print('Hello, %s!' % name)
        """)

        result = self.execute('snake hello')

        self.assertStderrEmpty(result)
        self.assertStdoutEqual(result, ['Hello, World!'])
        self.assertStatusEqual(result, 0)

        result = self.execute('snake hello name=Unittest')

        self.assertStderrEmpty(result)
        self.assertStdoutEqual(result, ['Hello, Unittest!'])
        self.assertStatusEqual(result, 0)

    def test_it_runs_namespaced_commands(self):
        self.use_snakefile("""
            from snake import *

            @namespace
            def name():

                @task
                def space():
                    sh('true')
        """)

        result = self.execute('snake name:space')

        self.assertStderrEmpty(result)
        self.assertStdoutEqual(result, ['true'])
        self.assertStatusEqual(result, 0)

    def test_it_runs_tasks_with_dependencies(self):
        self.use_snakefile("""
            from __future__ import print_function
            from snake import *

            @task(requires=['two', 'three'])
            def one():
                print('one')

            @task(requires=['three'])
            def two():
                print('two')

            @task
            def three():
                print('three')
        """)

        result = self.execute('snake one')

        self.assertStderrEmpty(result)
        self.assertStdoutEqual(result, ['three', 'two', 'one'])
        self.assertStatusEqual(result, 0)

    def test_it_has_shortcut_to_current_environment(self):
        import os
        os.environ['THING'] = 'hey'

        self.use_snakefile("""
            from __future__ import print_function
            from snake import *

            @task
            def check():
                print(env.get('THING'))
        """)

        result = self.execute('snake check')

        self.assertStderrEmpty(result)
        self.assertStdoutEqual(result, ['hey'])
        self.assertStatusEqual(result, 0)

    def test_it_exits_when_shell_command_fails(self):
        self.use_snakefile("""
            from snake import *

            @task
            def test():
                sh('blah')
        """)

        result = self.execute('snake test')

        self.assertStderrMatches(result, r'blah.* not found')
        self.assertStdoutEqual(result, ['blah'])
        self.assertStatusEqual(result, 1)

    def test_it_displays_all_available_tasks(self):
        self.use_snakefile("""
            from snake import *

            @namespace
            def sub():

                @task
                def one():
                    '''One'''

                @task
                def two():
                    '''Two'''

            @task
            def three():
                '''Three'''
        """)

        result = self.execute('snake -T')

        expected = [
            'snake sub:one  # One',
            'snake sub:two  # Two',
            'snake three    # Three',
        ]

        self.assertStderrEmpty(result)
        self.assertStdoutEqual(result, expected)
        self.assertStatusEqual(result, 0)

    def test_it_reports_exception_with_terse_stack_trace(self):
        self.use_snakefile("""
            from snake import *

            @task
            def bad():
                raise Exception("Bad task")
        """)

        result = self.execute('snake bad')

        self.assertStdoutEmpty(result)
        self.assertStderrMatches(result, r'^Bad task$')
        self.assertStderrMatches(result, r"Snakefile:5:in `bad'$")
        self.assertStderrMatches(result, r"^\(See full trace by running task with --trace\)$")
        self.assertStderrDoesNotMatch(result, r"application.py:\d+:")
        self.assertStatusEqual(result, 1)

    def test_it_reports_full_stack_trace_with_option(self):
        self.use_snakefile("""
            from snake import *

            @task
            def bad():
                raise Exception("Bad task")
        """)

        result = self.execute('snake bad --trace')

        self.assertStdoutEmpty(result)
        self.assertStderrMatches(result, r'^Bad task$')
        self.assertStderrMatches(result, r"Snakefile:5:in `bad'$")
        self.assertStderrMatches(result, r"application.py:\d+:")
        self.assertStatusEqual(result, 1)
