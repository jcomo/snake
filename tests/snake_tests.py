from tests.utils import IntegrationTest


class SnakeTests(IntegrationTest):
    def test_it_exits_with_error_when_no_snakefile_found(self):
        result = self.execute('snake')

        self.assertStatusEqual(result, 1)
        self.assertStdoutEmpty(result)
        self.assertStderrMatches(result, r'^snake aborted!$')
        self.assertStderrMatches(result, r'^No Snakefile found$')

    def test_it_exits_with_error_when_task_name_not_found(self):
        self.use_snakefile("""
            from snake import *

            @task("Do something")
            def something():
                pass
        """)

        result = self.execute('snake blah')

        self.assertStdoutEmpty(result)
        self.assertStderrMatches(result, "Don't know how to build task: blah")
        self.assertStatusEqual(result, 1)

    def test_it_runs_default_task_when_none_specified(self):
        self.use_snakefile("""
            from snake import *

            default = 'greet'

            @task("Greet")
            def greet():
                print 'hi'
        """)

        result = self.execute('snake')

        self.assertStderrEmpty(result)
        self.assertStdoutEqual(result, ['hi'])
        self.assertStatusEqual(result, 0)

    def test_it_outputs_command_when_running_shell(self):
        self.use_snakefile("""
            from snake import *

            @task("Test")
            def test():
                sh('true')
        """)

        result = self.execute('snake test')

        self.assertStderrEmpty(result)
        self.assertStdoutEqual(result, ['true'])
        self.assertStatusEqual(result, 0)

    def test_it_passes_arguments_to_tasks(self):
        self.use_snakefile("""
            from snake import *

            @task("Say hello")
            def hello(name='World'):
                print 'Hello, %s!' % name
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

                @task("Does stuff")
                def space():
                    sh('true')
        """)

        result = self.execute('snake name:space')

        self.assertStderrEmpty(result)
        self.assertStdoutEqual(result, ['true'])
        self.assertStatusEqual(result, 0)

    def test_it_has_shortcut_to_current_environment(self):
        import os
        os.environ['THING'] = 'hey'

        self.use_snakefile("""
            from snake import *

            @task("Check environment")
            def check():
                print env.get('THING')
        """)

        result = self.execute('snake check')

        self.assertStderrEmpty(result)
        self.assertStdoutEqual(result, ['hey'])
        self.assertStatusEqual(result, 0)

    def test_it_exits_when_shell_command_fails(self):
        self.use_snakefile("""
            from snake import *

            @task("Test")
            def test():
                sh('blah')
        """)

        result = self.execute('snake test')

        self.assertStderrMatches(result, r'blah.*command not found')
        self.assertStdoutEqual(result, ['blah'])
        self.assertStatusEqual(result, 1)

    def test_it_displays_all_available_tasks(self):
        self.use_snakefile("""
            from snake import *

            @namespace
            def sub():

                @task("One")
                def one():
                    pass

                @task("Two")
                def two():
                    pass

            @task("Three")
            def three():
                pass
        """)

        result = self.execute('snake -T')

        expected = [
            'sub:one      # One',
            'sub:two      # Two',
            'three        # Three',
        ]

        self.assertStderrEmpty(result)
        self.assertStdoutEqual(result, expected)
        self.assertStatusEqual(result, 0)

    def test_it_reports_exception_with_terse_stack_trace(self):
        self.use_snakefile("""
            from snake import *

            @task("Bad")
            def bad():
                raise Exception("Bad task")
        """)

        result = self.execute('snake bad')

        self.assertStdoutEmpty(result)
        self.assertStderrMatches(result, r'^Bad task$')
        self.assertStderrMatches(result, r"Snakefile:5:in `bad'$")
        self.assertStderrMatches(result, r"^\(See full trace by running task with --trace\)$")
        self.assertStderrDoesNotMatch(result, r"snake.py:\d+:")
        self.assertStatusEqual(result, 1)

    def test_it_reports_full_stack_trace_with_option(self):
        self.use_snakefile("""
            from snake import *

            @task("Bad")
            def bad():
                raise Exception("Bad task")
        """)

        result = self.execute('snake bad --trace')

        self.assertStdoutEmpty(result)
        self.assertStderrMatches(result, r'^Bad task$')
        self.assertStderrMatches(result, r"Snakefile:5:in `bad'$")
        self.assertStderrMatches(result, r"snake.py:\d+:")
        self.assertStatusEqual(result, 1)
