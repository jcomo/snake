from mock import Mock, patch
from unittest2 import TestCase

from snake.application import Application
from snake.shell import ShellWrapper, CommandFailedException


class ShellWrapperTests(TestCase):
    def setUp(self):
        super(ShellWrapperTests, self).setUp()
        self.logger = Mock(spec=Application)
        self.shell = ShellWrapper(self.logger)

    def test_it_prints_and_executes_command(self):
        with patch('snake.shell.call') as mock_call:
            mock_call.return_value = 0
            self.shell.execute('echo hello world')

            mock_call.assert_called_once_with('echo hello world', shell=True)
            self.logger.info.assert_called_once_with('echo hello world')

    def test_it_exits_on_unsuccessful_command(self):
        with patch('snake.shell.call') as mock_call:
            mock_call.return_value = 1

            with self.assertRaisesRegexp(CommandFailedException, r'failed with status \(1\).*echo'):
                self.shell.execute('echo hello world')
