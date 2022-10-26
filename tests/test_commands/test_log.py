from unittest import TestCase
from unittest.mock import Mock, patch

from commands import Log
from interfaces import ICommand


class TestLog(TestCase):
    @patch('builtins.print')
    def test_log_command(self, mocked_print):
        """Реализовать Команду, которая записывает информацию о выброшенном исключении в лог."""
        cmd = Mock(ICommand)
        exc = Exception("Error")

        log_cmd = Log(cmd, exc)
        log_cmd.execute()
        mocked_print.assert_called_once_with('An error has occurred.\nCmd: ICommand\nException: Error')
