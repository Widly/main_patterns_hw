import math
from collections.abc import Iterable
from typing import Union

import numpy as np

from exceptions import CommandException
from interfaces import ICommand, IMovable, IRotatable, IFuelable, IVelocityChangeable


class MacroCommand(ICommand):
    def __init__(self, commands: Iterable[ICommand]):
        self.commands = commands

    def execute(self) -> None:
        try:
            for cmd in self.commands:
                cmd.execute()
        except Exception as e:
            raise CommandException(e)


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


class ChangeVelocity(ICommand):
    def __init__(self, velocity_changeable: IVelocityChangeable):
        self.obj = velocity_changeable

    def execute(self) -> None:
        try:
            velocity = self.obj.get_velocity()
        except:
            # Если у объекта нельзя получить вектор скорости, значит он не может двигаться. Завершаем выполнение.
            return
        angle = self.obj.get_angle()
        velocity_modulus = math.sqrt(sum([a**2 for a in velocity]))
        self.obj.set_velocity(np.array([
            round(velocity_modulus * math.cos(angle)),
            round(velocity_modulus * math.sin(angle))
        ]))


class RotateWithChangeVelocity(ICommand):
    def __init__(self, obj: Union[IRotatable, IVelocityChangeable]):
        self.obj = obj

    def execute(self) -> None:
        MacroCommand([
            Rotate(self.obj),
            ChangeVelocity(self.obj)
        ]).execute()
