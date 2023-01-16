from typing import Iterable

from exceptions import CommandException
from .interfaces import ICommand


class MacroCommand(ICommand):
    def __init__(self, commands: Iterable[ICommand]):
        self.commands = commands

    def execute(self) -> None:
        try:
            for cmd in self.commands:
                cmd.execute()
        except Exception as e:
            raise CommandException(e)
