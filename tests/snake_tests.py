from tests.utils import IntegrationTest


class SnakeTests(IntegrationTest):
    def test_it_exits_with_error_when_no_snakefile_found(self):
        result = self.execute('snake')

        self.assertStatusEqual(result, 1)
        self.assertStdoutEmpty(result)
        self.assertStderrEqual(result, ["No Snakefile found"])

    def test_it_exits_with_error_when_task_name_not_found(self):
        self.use_snakefile("""
            from snake import *

            @task("Do something")
            def something():
                pass
        """)

        result = self.execute('snake blah')

        self.assertStatusEqual(result, 1)
        self.assertStdoutEmpty(result)
        self.assertStderrEqual(result, ["Don't know how to build task: blah"])

    def test_it_runs_default_task_when_none_specified(self):
        self.use_snakefile("""
            from snake import *

            @task("Default")
            def default():
                print 'hi'
        """)

        result = self.execute('snake')

        self.assertStatusEqual(result, 0)
        self.assertStdoutEqual(result, ['hi'])
        self.assertStderrEmpty(result)

    def test_it_outputs_command_when_running_shell(self):
        self.use_snakefile("""
            from snake import *

            @task("Default")
            def default():
                sh('true')
        """)

        result = self.execute('snake')

        self.assertStatusEqual(result, 0)
        self.assertStdoutEqual(result, ['true'])
        self.assertStderrEmpty(result)

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

            @task("Default")
            def default():
                sh('blah')
        """)

        result = self.execute('snake')

        self.assertStatusEqual(result, 127)
        self.assertStdoutEqual(result, ['blah'])
        self.assertStderrMatchesLine(result, r'blah.*command not found')
