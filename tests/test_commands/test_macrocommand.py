from unittest import TestCase
from unittest.mock import Mock

from commands import MacroCommand
from exceptions import CommandException
from interfaces import ICommand


class TestMacroCommand(TestCase):
    def test_command(self):
        """
        Тестируем, что CommandException.execute запускает последовательный вызов команд, определенных при инициализации.
        """
        cmd_1 = Mock(ICommand)
        cmd_2 = Mock(ICommand)
        cmd_3 = Mock(ICommand)

        macrocommand = MacroCommand([cmd_1, cmd_2, cmd_3])
        macrocommand.execute()
        cmd_1.execute.assert_called_once()
        cmd_2.execute.assert_called_once()
        cmd_3.execute.assert_called_once()

    def test_one_of_commands_error(self):
        """
        Тестируем, что в случае ошибки при вызове одной из команд, макрокоманда выбрасывает ошибку CommandException,
        а запуск следующих команд не осуществляется.
        """
        cmd_1 = Mock(ICommand)
        cmd_2 = Mock(ICommand)
        cmd_3 = Mock(ICommand)

        cmd_2.execute.side_effect = KeyError('Some key error')

        macrocommand = MacroCommand([cmd_1, cmd_2, cmd_3])
        with self.assertRaisesRegex(CommandException, 'Some key error'):
            macrocommand.execute()

        cmd_1.execute.assert_called_once()
        # Команда cmd_2 запустилась, но выбросила ошибку, поэтому следующая команда (cmd_3) не вызывалась
        cmd_2.execute.assert_called_once()
        cmd_3.execute.assert_not_called()







