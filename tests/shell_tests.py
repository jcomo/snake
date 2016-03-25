from mock import Mock, patch
from unittest import TestCase

from snake.snake import Snake
from snake.shell import ShellWrapper


class ShellWrapperTests(TestCase):
    def setUp(self):
        super(ShellWrapperTests, self).setUp()
        self.app = Mock(spec=Snake)
        self.shell = ShellWrapper(self.app)

    def test_it_prints_and_executes_command(self):
        with patch('snake.shell.call') as mock_call:
            mock_call.return_value = 0
            self.shell.execute('echo hello world')

            mock_call.assert_called_once_with('echo hello world', shell=True)
            self.app.info.assert_called_once_with('echo hello world')

    def test_it_exits_on_unsuccessful_command(self):
        with patch('snake.shell.call') as mock_call:
            mock_call.return_value = 1
            self.shell.execute('echo hello world')

        self.app.abort.assert_called_once_with(1)
