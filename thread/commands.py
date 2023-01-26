from queue import Queue, Empty
from threading import Thread

from features.base.commands import LambdaCommand
from features.base.interfaces import ICommand
from iocs import IoC


class ThreadRepeatedCommand(ICommand):
    def __init__(self, cmd):
        self.cmd = cmd

    def execute(self) -> None:
        self.cmd.execute()
        IoC.resolve('Thread.Put', self).execute()


class StartThreadCommand(ICommand):
    """
    Команда запускает поток который выполняет команды из очереди. Команды кладутся в очередь другими потоками.
    Предполагается, что в качестве стратегии разрешения зависимостей IoC используется
    HierarchicalScopeBasedDependencyStrategy.
    """

    def __init__(self, thread_id):
        self.thread_id = thread_id
        self._hard_stop = False
        self._soft_stop = False

    def hard_stop(self):
        self._hard_stop = True

    def soft_stop(self):
        self._soft_stop = True

    def execute(self) -> None:
        q = Queue()

        IoC.resolve('Scopes.New', self.thread_id, IoC.resolve('Scopes.Current').id)
        IoC.resolve('Scopes.Current.Set', self.thread_id).execute()

        IoC.resolve(
            'IoC.Register',
            'Thread.Put',
            lambda cmd: LambdaCommand(lambda: q.put(cmd))
        ).execute()

        IoC.resolve(
            'IoC.Register',
            'Thread.PutWithRepeat',
            lambda cmd: IoC.resolve('Thread.Put', ThreadRepeatedCommand(cmd))
        ).execute()

        IoC.resolve(
            'IoC.Register',
            'Thread.HardStop',
            lambda: LambdaCommand(self.hard_stop)
        ).execute()

        IoC.resolve(
            'IoC.Register',
            'Thread.SoftStop',
            lambda: LambdaCommand(self.soft_stop)
        ).execute()

        def run():
            while True:
                if self._hard_stop:
                    # В случае Hard Stop сразу выходим из цикла - поток завершается
                    break

                if self._soft_stop:
                    # В случае Soft Stop выходим из цикла в случае отсутствия команд в очереди
                    try:
                        cmd = q.get_nowait()
                    except Empty:
                        break
                else:
                    # Обычный режим работы потока - ожидаем команды из очереди
                    cmd = q.get()

                # Инициализация скоупа данного потока
                IoC.resolve('Scopes.Current.Set', self.thread_id).execute()

                try:
                    cmd.execute()
                except Exception as e:
                    # Обрабатываем все ошибки возникающие при выполнении команд с помощью Обрабочика ошибок
                    # Выброс исключения из команды не должен прерывать выполнение потока
                    try:
                        exc_handler = IoC.resolve('ExceptionHandler')
                        exc_handler.handle(cmd, e)
                    except Exception as unhandled_e:
                        print(f'Unhandled exception has occured: {unhandled_e} for {cmd}')
                q.task_done()

        thread = Thread(
            target=run,
            daemon=True
        )

        IoC.resolve('IoC.Register', 'Thread', lambda: thread).execute()
        thread.start()


class StartThreadCommandPlugin(ICommand):
    def execute(self) -> None:
        IoC.resolve(
            'IoC.Register',
            'Thread.Start',
            lambda thread_id: StartThreadCommand(thread_id)
        ).execute()
