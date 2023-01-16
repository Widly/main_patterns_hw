from typing import Union

from exceptions import CommandException
from features.base.commands import MacroCommand
from features.base.interfaces import ICommand
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


class MoveWithFuel(ICommand):
    def __init__(self, obj: Union[IMovable, IFuelable]):
        self.obj = obj

    def execute(self) -> None:
        MacroCommand([
            CheckFuel(self.obj),
            Move(self.obj),
            BurnFuel(self.obj)
        ]).execute()
