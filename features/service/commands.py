from features.base.interfaces import ICommand


class Log(ICommand):
    def __init__(self, cmd: ICommand, exc: Exception):
        self.cmd = cmd
        self.exc = exc

    def execute(self) -> None:
        print(f'An error has occurred.\nCmd: {self.cmd.__class__.__name__}\nException: {self.exc}')


class Retry(ICommand):
    def __init__(self, cmd: ICommand):
        self.cmd = cmd

    def execute(self) -> None:
        self.cmd.execute()


class DoubleRetry(ICommand):
    def __init__(self, cmd: ICommand):
        self.cmd = cmd

    def execute(self) -> None:
        self.cmd.execute()
