from features.base.interfaces import ICommand
from iocs import IoC
from iocs.scope_based.event_loop import CommandExecutorThread


class StartThreadCommand(ICommand):
    """
    Команда запускает поток CommandExecutorThread
    """
    def execute(self) -> None:
        parent_scope = IoC.resolve('Scopes.Current')
        thread = CommandExecutorThread(parent_scope=parent_scope, daemon=True)
        IoC.resolve('IoC.Register', 'Thread', lambda: thread).execute()
        thread.start()
