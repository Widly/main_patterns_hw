import numpy as np

from exceptions import CommandException
from features.base.commands import GetProperty, SetProperty
from features.base.interfaces import ICommand
from iocs import IoC
from .interfaces import IMovable, IFuelable, IMovementStartable


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


class StartMovement(ICommand):
    def __init__(self, obj: IMovementStartable, initial_velocity: list):
        self.initial_velocity = np.array(initial_velocity)
        self.obj = obj

    def execute(self) -> None:
        self.obj.set_velocity(self.initial_velocity)

        operation = IoC.resolve(f'Operations.Movement', self.obj.get_object())
        IoC.resolve('Queue.PutWithRepeat', operation).execute()


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
            lambda obj: GetProperty(obj, "velocity").execute()  # здесь может быть другая логика
        ).execute()

        IoC.resolve(
            'IoC.Register',
            'Commands.Move',
            lambda obj: Move(IoC.resolve("Adapter", IMovable, obj))
        ).execute()

        IoC.resolve(
            'IoC.Register',
            'IMovementStartable:velocity.set',
            lambda obj, value: SetProperty(obj, "velocity", value)
        ).execute()

        IoC.resolve(
            'IoC.Register',
            'IMovementStartable:object.get',
            lambda obj: obj
        ).execute()

        IoC.resolve(
            'IoC.Register',
            'Commands.StartMovement',
            lambda obj, *args, **kwargs: StartMovement(IoC.resolve("Adapter", IMovementStartable, obj), *args, **kwargs)
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
