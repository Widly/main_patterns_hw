from queue import Empty
from threading import Thread

from iocs import IoC


class CommandExecutorThread(Thread):
    """
    Поток выполняет команды из очереди. Команды кладутся в очередь другим потоком. Предполагается, что в качестве
    стратегии разрешения зависимостей IoC используется HierarchicalScopeBasedDependencyStrategy.
    """

    def __init__(self, *args, parent_scope, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent_scope = parent_scope

    @property
    def hard_stop(self):
        try:
            return IoC.resolve('Thread.HardStop')
        except KeyError:
            return False

    @property
    def soft_stop(self):
        try:
            return IoC.resolve('Thread.SoftStop')
        except KeyError:
            return False

    def run(self):
        # Инициализация скоупа данного потока
        thread_scope = IoC.resolve('Scopes.New', self.parent_scope)
        IoC.resolve('Scopes.Current.Set', thread_scope).execute()

        # Получаем Очередь и Обработчик ошибок
        q = IoC.resolve('Queue')
        exc_handler = IoC.resolve('ExceptionHandler')

        while True:
            if self.hard_stop:
                # В случае Hard Stop сразу выходим из цикла - поток завершается
                break

            if self.soft_stop:
                # В случае Soft Stop выходим из цикла в случае отсутствия команд в очереди
                try:
                    cmd = q.get_nowait()
                except Empty:
                    break
            else:
                # Обычный режим работы потока - ожидаем команды из очереди
                cmd = q.get()

            try:
                cmd.execute()
            except Exception as e:
                # Обрабатываем все ошибки возникающие при выполнении команд с помощью Обрабочика ошибок
                # Выброс исключения из команды не должен прерывать выполнение потока
                try:
                    exc_handler.handle(cmd, e)
                except Exception as unhandled_e:
                    print(f'Unhandled exception has occured: {unhandled_e} for {cmd}')
            q.task_done()
