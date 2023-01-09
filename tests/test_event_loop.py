from queue import Queue
from threading import active_count
from unittest import TestCase
from unittest.mock import Mock, patch

from commands import ICommand, StartThreadCommand, HardStopThreadCommand, SoftStopThreadCommand
from exception_handler import ExceptionHandler
from iocs import IoC
from iocs.scope_based import InitScopesCommand


class TestEventLoop(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        InitScopesCommand().execute()

    def setUp(self) -> None:
        # Создаем новый скоуп чтобы не вносить зависимости в Root скоуп
        scope = IoC.resolve('Scopes.New', IoC.resolve('Scopes.Root'))
        IoC.resolve('Scopes.Current.Set', scope).execute()

        # Создаем Очередь задач и Обработчик ошибок
        queue = Queue()
        exc_handler = ExceptionHandler()
        IoC.resolve('IoC.Register', 'Queue', lambda: queue).execute()
        IoC.resolve('IoC.Register', 'ExceptionHandler', lambda: exc_handler).execute()

        self.queue = queue
        self.exc_handler = exc_handler

    @classmethod
    def tearDownClass(cls) -> None:
        IoC.resolve('Scopes.Current.Set', IoC.resolve('Scopes.Root')).execute()

    def test_start_thread_and_hard_stop(self):
        """Тест на запуск и Hard Stop потока"""
        self.assertEqual(1, active_count())
        StartThreadCommand().execute()
        self.assertEqual(2, active_count())  # Проверяем, что команда StartThreadCommand запускает новый поток

        test_cmd_1 = Mock(ICommand)
        test_cmd_2 = Mock(ICommand)

        self.queue.put(test_cmd_1)
        self.queue.put(HardStopThreadCommand())
        self.queue.put(test_cmd_2)  # Данная команда не должна выполниться исходя из логики Hard Stop

        thread = IoC.resolve('Thread')
        thread.join(timeout=5)

        self.assertEqual(1, active_count())  # Проверяем, что поток завершился
        test_cmd_1.execute.assert_called_once()
        test_cmd_2.execute.assert_not_called()

    def test_start_thread_and_soft_stop(self):
        """Тест на запуск и Soft Stop потока"""
        self.assertEqual(1, active_count())
        StartThreadCommand().execute()
        self.assertEqual(2, active_count())  # Проверяем, что команда StartThreadCommand запускает новый поток

        test_cmd_1 = Mock(ICommand)
        test_cmd_2 = Mock(ICommand)

        self.queue.put(test_cmd_1)
        self.queue.put(SoftStopThreadCommand())

        # Данная команда должна выполниться исходя из логики Soft Stop - выполняем все команды из очереди пока
        # очередь не освободится
        self.queue.put(test_cmd_2)

        thread = IoC.resolve('Thread')
        thread.join(timeout=5)

        self.assertEqual(1, active_count())  # Проверяем, что поток завершился
        test_cmd_1.execute.assert_called_once()
        test_cmd_2.execute.assert_called_once()

    @patch('exception_handler.ExceptionHandler.handle')
    def test_handle_command_exception(self, mocked_handle):
        """Проверяем, что выброс исключения из команды не прерывает выполнение потока"""
        StartThreadCommand().execute()

        test_cmd_1 = Mock(ICommand)
        cmd_error = ValueError("Error")
        test_cmd_1.execute.side_effect = cmd_error

        test_cmd_2 = Mock(ICommand)

        self.queue.put(test_cmd_1)  # Команда выбрасывающая исключение
        self.queue.put(test_cmd_2)
        self.queue.put(HardStopThreadCommand())

        thread = IoC.resolve('Thread')
        thread.join(timeout=5)

        self.assertEqual(1, active_count())  # Проверяем, что поток завершился
        mocked_handle.assert_called_once_with(test_cmd_1, cmd_error)  # Поток обработал исключение
        test_cmd_2.execute.assert_called_once()  # Поток запустил следуюшую команду из очереди
