from exceptions import CommandException
from features.base.commands import GetProperty, SetProperty
from features.base.interfaces import ICommand
from iocs import IoC
from .interfaces import IMovable, IFuelable


class Move(ICommand):
    def __init__(self, movable: IMovable):
        self.m = movable

    def execute(self):
        self.m.set_position(self.m.get_position() + self.m.get_velocity())


class CheckFuel(ICommand):
    def __init__(self, fuelable: IFuelable):
        self.obj = fuelable

    def execute(self) -> None:
        if self.obj.get_fuel_level() < self.obj.get_fuel_consumption():
            raise CommandException('Not enough fuel')


class BurnFuel(ICommand):
    def __init__(self, fuelable: IFuelable):
        self.obj = fuelable

    def execute(self) -> None:
        self.obj.set_fuel_level(self.obj.get_fuel_level() - self.obj.get_fuel_consumption())


class MoveCommandPluginCommand(ICommand):
    def execute(self) -> None:
        IoC.resolve(
            'IoC.Register',
            'IMovable:position.get',
            lambda obj: GetProperty(obj, "position").execute()
        ).execute()

        IoC.resolve(
            'IoC.Register',
            'IMovable:position.set',
            lambda obj, value: SetProperty(obj, "position", value)
        ).execute()

        IoC.resolve(
            'IoC.Register',
            'IMovable:velocity.get',
            lambda obj: GetProperty(obj, "velocity").execute()  # TODO здесь может быть другая логика
        ).execute()

        IoC.resolve(
            'IoC.Register',
            'Commands.Move',
            lambda obj: Move(IoC.resolve("Adapter", IMovable, obj))
        ).execute()


class FuelCommandsPluginCommand(ICommand):
    def execute(self) -> None:
        IoC.resolve(
            'IoC.Register',
            'IFuelable:fuel_level.get',
            lambda obj: GetProperty(obj, "fuel_level").execute()
        ).execute()

        IoC.resolve(
            'IoC.Register',
            'IFuelable:fuel_level.set',
            lambda obj, value: SetProperty(obj, "fuel_level", value)
        ).execute()

        IoC.resolve(
            'IoC.Register',
            'IFuelable:fuel_consumption.get',
            lambda obj: GetProperty(obj, "fuel_consumption").execute()
        ).execute()

        IoC.resolve(
            'IoC.Register',
            'Commands.CheckFuel',
            lambda obj: CheckFuel(IoC.resolve("Adapter", IFuelable, obj))
        ).execute()

        IoC.resolve(
            'IoC.Register',
            'Commands.BurnFuel',
            lambda obj: BurnFuel(IoC.resolve("Adapter", IFuelable, obj))
        ).execute()
