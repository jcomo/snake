from os import path, getcwd, chdir, makedirs, remove, environ as env
from re import search
from shutil import rmtree
from subprocess import Popen, PIPE
from time import time

from unittest import TestCase


class ProcessResult(object):
    def __init__(self, status, stdout, stderr):
        self.status = status
        self.stdout = stdout.strip().split('\n')
        self.stderr = stderr.strip().split('\n')


class IntegrationTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(IntegrationTest, cls).setUpClass()
        cls._sandbox_dir = '/tmp/snaketests_%d' % int(time())
        cls._current_dir = getcwd()

        cls._update_pythonpath_to_prefer_dev_version()
        cls._create_and_enter_sandbox()

    @classmethod
    def tearDownClass(cls):
        cls._leave_and_destroy_sandbox()
        super(IntegrationTest, cls).tearDownClass()

    def tearDown(self):
        self._remove_snakefile()
        super(IntegrationTest, self).tearDown()

    def assertStatusEqual(self, result, status):
        self.assertEqual(status, result.status)

    def assertStdoutEqual(self, result, expected):
        self.assertEqual(expected, result.stdout)

    def assertStderrEqual(self, result, expected):
        self.assertEqual(expected, result.stderr)

    def assertStdoutEmpty(self, result):
        self.assertEqual([''], result.stdout)

    def assertStderrEmpty(self, result):
        self.assertEqual([''], result.stderr)

    def assertStdoutMatchesLine(self, result, pattern):
        self._assertOutputMatchesLine(result.stdout, pattern)

    def assertStderrMatchesLine(self, result, pattern):
        self._assertOutputMatchesLine(result.stderr, pattern)

    def _assertOutputMatchesLine(self, output, pattern):
        for line in output:
            if search(pattern, line):
                break
        else:
            friendly_output = repr('\n'.join(output))
            self.fail("No match found for %s in %s" % (repr(pattern), friendly_output))

    def use_snakefile(self, contents):
        with open('Snakefile', 'w') as f:
            f.write(self._remove_indentation_padding(contents))

    def execute(self, command):
        p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()

        return ProcessResult(p.returncode, stdout, stderr)

    def _remove_indentation_padding(self, contents):
        contents = contents.lstrip('\n')
        padding = len(contents) - len(contents.lstrip(' '))

        return '\n'.join(line[padding:] for line in contents.split('\n'))

    def _remove_snakefile(self):
        try:
            remove('Snakefile')
        except OSError:
            pass

    @classmethod
    def _update_pythonpath_to_prefer_dev_version(cls):
        env['PYTHONPATH'] = cls._current_dir + env.get('PYTHONPATH', '')
        env['PATH'] = path.join(cls._current_dir, 'bin') + ':' + env.get('PATH', '')

    @classmethod
    def _create_and_enter_sandbox(cls):
        makedirs(cls._sandbox_dir, mode=0o755)
        chdir(cls._sandbox_dir)

    @classmethod
    def _leave_and_destroy_sandbox(cls):
        chdir(cls._current_dir)
        rmtree(cls._sandbox_dir)


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
