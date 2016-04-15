from mock import Mock, patch
from unittest2 import TestCase

from snake.application import Application
from snake.shell import ShellWrapper, CommandFailedException


class ShellWrapperTests(TestCase):
    def setUp(self):
        super(ShellWrapperTests, self).setUp()
        self.logger = Mock(spec=Application)
        self.shell = ShellWrapper(self.logger)

    @patch('snake.shell.call')
    def test_it_prints_and_executes_command(self, mock_call):
            mock_call.return_value = 0
            self.shell.execute('echo hello world')

            mock_call.assert_called_once_with('echo hello world', shell=True)
            self.logger.info.assert_called_once_with('echo hello world')

    @patch('snake.shell.call')
    def test_it_exits_on_unsuccessful_command(self, mock_call):
        mock_call.return_value = 1

        with self.assertRaisesRegexp(CommandFailedException, r'failed with status \(1\).*echo'):
            self.shell.execute('echo hello world')

    @patch('snake.shell.call')
    def test_it_does_not_raise_and_returns_status_when_silent(self, mock_call):
        mock_call.return_value = 1

        status = self.shell.execute('echo hello world', silent=True)
        self.assertEqual(1, status)
