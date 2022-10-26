from unittest import TestCase
from unittest.mock import Mock

from interfaces import ICommand
from commands import Retry


class TestRetry(TestCase):
    def test_command(self):
        """Реализовать Команду, которая повторяет Команду, выбросившую исключение."""
        cmd = Mock(ICommand)

        log_cmd = Retry(cmd)
        log_cmd.execute()
        cmd.execute.assert_called_once()
