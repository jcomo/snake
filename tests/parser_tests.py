from unittest import TestCase

from snake.parser import ApplicationArgsParser


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
        _, _, opts = self._parse_command_line('-f file --trace')

        self.assertEqual('file', opts.filename)
        self.assertEqual(True, opts.trace)

    def test_it_parses_everything_together(self):
        command = '-f file bootstrap install token=abc dir=env'

        tasks, args, opts = self._parse_command_line(command)

        self.assertEqual(['bootstrap', 'install'], tasks)
        self.assertEqual({'token': 'abc', 'dir': 'env'}, args)
        self.assertEqual('file', opts.filename)

    def _parse_command_line(self, line):
        return ApplicationArgsParser.parse(line.split(' '))
