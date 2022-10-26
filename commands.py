from interfaces import ICommand, IMovable, IRotatable


class Move(ICommand):
    def __init__(self, movable: IMovable):
        self.m = movable

    def execute(self):
        self.m.set_position(self.m.get_position() + self.m.get_velocity())


class Rotate(ICommand):
    def __init__(self, rotatable: IRotatable):
        self.r = rotatable

    def execute(self):
        self.r.set_direction(
            (self.r.get_direction() + self.r.get_angular_velocity()) % self.r.get_directions_number()
        )


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
