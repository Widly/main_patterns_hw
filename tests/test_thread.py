from threading import active_count
from unittest import TestCase
from unittest.mock import Mock, patch

from exception_handler import ExceptionHandler
from features.base.interfaces import ICommand
from iocs import IoC
from iocs.scope_based_strategy import InitScopesCommand
from thread.commands import StartThreadCommand


class TestEventLoop(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        InitScopesCommand().execute()

    def setUp(self) -> None:
        # Создаем новый скоуп чтобы не вносить зависимости в Root скоуп
        IoC.resolve('Scopes.New', 'scope-id')
        IoC.resolve('Scopes.Current.Set', 'scope-id').execute()

        # Создаем обработчик ошибок
        exc_handler = ExceptionHandler()
        IoC.resolve('IoC.Register', 'ExceptionHandler', lambda: exc_handler).execute()
        self.exc_handler = exc_handler

    def tearDown(self) -> None:
        IoC.resolve('Scopes.Current.Set', 'ROOT').execute()
        IoC.resolve('Scopes.Clear').execute()

    def test_start_thread_and_hard_stop(self):
        """Тест на запуск и Hard Stop потока"""
        self.assertEqual(1, active_count())
        StartThreadCommand('thread-id').execute()
        self.assertEqual(2, active_count())  # Проверяем, что команда StartThreadCommand запускает новый поток

        test_cmd_1 = Mock(ICommand)
        test_cmd_2 = Mock(ICommand)

        IoC.resolve('Thread.Put', test_cmd_1).execute()
        IoC.resolve(
            'Thread.Put',
            IoC.resolve('Thread.HardStop')
        ).execute()

        # Данная команда не должна выполниться исходя из логики Hard Stop
        IoC.resolve('Thread.Put', test_cmd_2).execute()

        thread = IoC.resolve('Thread')
        thread.join(timeout=5)

        self.assertEqual(1, active_count())  # Проверяем, что поток завершился
        test_cmd_1.execute.assert_called_once()
        test_cmd_2.execute.assert_not_called()

    def test_start_thread_and_soft_stop(self):
        """Тест на запуск и Soft Stop потока"""
        self.assertEqual(1, active_count())
        StartThreadCommand('thread-id').execute()
        self.assertEqual(2, active_count())  # Проверяем, что команда StartThreadCommand запускает новый поток

        test_cmd_1 = Mock(ICommand)
        test_cmd_2 = Mock(ICommand)

        IoC.resolve('Thread.Put', test_cmd_1).execute()
        IoC.resolve(
            'Thread.Put',
            IoC.resolve('Thread.SoftStop')
        ).execute()

        # Данная команда должна выполниться исходя из логики Soft Stop - выполняем все команды из очереди пока
        # очередь не освободится
        IoC.resolve('Thread.Put', test_cmd_2).execute()

        thread = IoC.resolve('Thread')
        thread.join(timeout=5)

        self.assertEqual(1, active_count())  # Проверяем, что поток завершился
        test_cmd_1.execute.assert_called_once()
        test_cmd_2.execute.assert_called_once()

    @patch('exception_handler.ExceptionHandler.handle')
    def test_handle_command_exception(self, mocked_handle):
        """Проверяем, что выброс исключения из команды не прерывает выполнение потока"""
        StartThreadCommand('thread-id').execute()

        test_cmd_1 = Mock(ICommand)
        cmd_error = ValueError("Error")
        test_cmd_1.execute.side_effect = cmd_error

        test_cmd_2 = Mock(ICommand)

        IoC.resolve('Thread.Put', test_cmd_1).execute()  # Команда выбрасывающая исключение
        IoC.resolve('Thread.Put', test_cmd_2).execute()
        IoC.resolve(
            'Thread.Put',
            IoC.resolve('Thread.HardStop')
        ).execute()

        thread = IoC.resolve('Thread')
        thread.join(timeout=5)

        self.assertEqual(1, active_count())  # Проверяем, что поток завершился
        mocked_handle.assert_called_once_with(test_cmd_1, cmd_error)  # Поток обработал исключение
        test_cmd_2.execute.assert_called_once()  # Поток запустил следуюшую команду из очереди
