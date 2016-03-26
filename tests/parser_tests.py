from unittest import TestCase

from snake.parser import CommandLineParser


class CommandLineParserTests(TestCase):
    def test_it_parses_task_names(self):
        tasks, _, _ = self._parse_command_line('bootstrap install')

        self.assertEqual(['bootstrap', 'install'], tasks)

    def test_it_parses_keyword_args(self):
        _, args, _ = self._parse_command_line('token=abc test=yes')

        expected = {
            'token': 'abc',
            'test': 'yes',
        }

        self.assertEqual(expected, args)

    def test_it_parses_flag_options(self):
        _, _, flags = self._parse_command_line('-T --verbose --exclude=env')

        expected = {
            'T': True,
            'verbose': True,
            'exclude': 'env',
        }

        self.assertEqual(expected, flags)

    def test_it_parses_everything_together(self):
        command = '--verbose bootstrap install token=abc dir=env'

        tasks, args, flags = self._parse_command_line(command)

        self.assertEqual(['bootstrap', 'install'], tasks)
        self.assertEqual({'token': 'abc', 'dir': 'env'}, args)
        self.assertEqual({'verbose': True}, flags)

    def test_it_raises_assertion_when_flags_specified_after_tasks(self):
        with self.assertRaisesRegexp(AssertionError, 'flags must be specified before'):
            self._parse_command_line('--thing task -T')

    def _parse_command_line(self, line):
        return CommandLineParser.parse(line.split(' '))
