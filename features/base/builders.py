from features.base.commands import MacroCommand
from features.base.interfaces import UObject
from iocs import IoC


class OperationBuilder:
    def __init__(self, name):
        self.operation_name = name

    def build(self, obj: UObject):
        command_names = IoC.resolve(f'{self.operation_name}.Description')
        commands = [IoC.resolve(c, obj) for c in command_names]
        return MacroCommand(commands)
