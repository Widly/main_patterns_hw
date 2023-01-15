from features.base.interfaces import ICommand
from iocs import IoC


class HardStopThreadCommand(ICommand):
    """
    Команда осуществляет Hard Stop потока CommandExecutorThread
    """

    def execute(self) -> None:
        IoC.resolve('IoC.Register', 'Thread.HardStop', lambda: True).execute()


class SoftStopThreadCommand(ICommand):
    """
    Команда осуществляет Soft Stop потока CommandExecutorThread
    """

    def execute(self) -> None:
        IoC.resolve('IoC.Register', 'Thread.SoftStop', lambda: True).execute()
