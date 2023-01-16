from unittest import TestCase
from unittest.mock import Mock

from features.service.commands import Log, Retry, DoubleRetry
from features.base.interfaces import ICommand
from exception_handler import ExceptionHandler


class TestExceptionHandler(TestCase):
    def setUp(self) -> None:
        self.queue = []  # Очередь
        self.exc_handler = ExceptionHandler()  # Обработчик исключений

    def test_5(self):
        """5. Реализовать обработчик исключения, который ставит Команду, пишущую в лог в очередь Команд."""
        # Определяем правила для обработчика исключений
        self.exc_handler.setup(ICommand, KeyError, lambda _cmd, _exc: self.queue.append(Log(_cmd, _exc)))

        # Команда, которая будет выбрасывать исключение
        cmd = Mock(ICommand)
        cmd_error = KeyError("Wrong key")
        cmd.execute.side_effect = cmd_error

        # Запускаем команду
        try:
            cmd.execute()
        except Exception as exc:
            self.exc_handler.handle(cmd, exc)

        # Проверяем, что в очередь попала команда Log
        cmd_from_queue = self.queue.pop(0)
        self.assertIsInstance(cmd_from_queue, Log)
        self.assertEqual(cmd_from_queue.cmd, cmd)
        self.assertEqual(cmd_from_queue.exc, cmd_error)

    def test_7(self):
        """
        7. Реализовать обработчик исключения, который ставит в очередь Команду - повторитель команды, выбросившей
        исключение.
        """
        # Определяем правила для обработчика исключений
        self.exc_handler.setup(ICommand, None, lambda _cmd, _exc: self.queue.append(Retry(_cmd)))

        # Команда, которая будет выбрасывать исключение
        cmd = Mock(ICommand)
        cmd_error = ValueError("Error")
        cmd.execute.side_effect = cmd_error

        # Запускаем команду
        try:
            cmd.execute()
        except Exception as exc:
            self.exc_handler.handle(cmd, exc)

        # Проверяем, что в очередь попала команда Retry
        cmd_from_queue = self.queue.pop(0)
        self.assertIsInstance(cmd_from_queue, Retry)
        self.assertEqual(cmd_from_queue.cmd, cmd)

    def test_8(self):
        """
        8. С помощью Команд из пункта 4 и пункта 6 реализовать следующую обработку исключений:
        при первом выбросе исключения повторить команду, при повторном выбросе исключения записать информацию в лог.
        """
        # Определяем правила для обработчика исключений
        self.exc_handler.setup(ICommand, None, lambda _cmd, _exc: self.queue.append(Retry(_cmd)))
        self.exc_handler.setup(Retry, None, lambda _cmd, _exc: self.queue.append(Log(_cmd, _exc)))

        # Команда, которая будет выбрасывать исключение
        cmd = Mock(ICommand)
        cmd_error = ValueError("Error")
        cmd.execute.side_effect = cmd_error

        # Запускаем команды из очереди. ExceptionHandler кладет в очередь новые команды
        # Проверяем цепочку ICommand -> Retry -> Log
        for _ in range(2):
            try:
                cmd.execute()
            except Exception as exc:
                self.exc_handler.handle(cmd, exc)
                cmd = self.queue.pop(0)  # Берем следующую команду из очереди

        self.assertIsInstance(cmd, Log)

    def test_9(self):
        """9. Реализовать стратегию обработки исключения - повторить два раза, потом записать в лог."""
        # Определяем правила для обработчика исключений
        self.exc_handler.setup(ICommand, None, lambda _cmd, _exc: self.queue.append(DoubleRetry(_cmd)))
        self.exc_handler.setup(DoubleRetry, None, lambda _cmd, _exc: self.queue.append(Retry(_cmd)))
        self.exc_handler.setup(Retry, None, lambda _cmd, _exc: self.queue.append(Log(_cmd, _exc)))

        # Команда, которая будет выбрасывать исключение
        cmd = Mock(ICommand)
        cmd_error = ValueError("Error")
        cmd.execute.side_effect = cmd_error

        # Запускаем команды из очереди. ExceptionHandler кладет в очередь новые команды
        # Проверяем цепочку ICommand -> DoubleRetry -> Retry -> Log
        for _ in range(3):
            try:
                cmd.execute()
            except Exception as exc:
                self.exc_handler.handle(cmd, exc)
                cmd = self.queue.pop(0)  # Берем следующую команду из очереди

        self.assertIsInstance(cmd, Log)
