import math
from typing import Union

import numpy as np

from features.base.commands import MacroCommand
from features.base.interfaces import ICommand
from features.rotation.interfaces import IVelocityChangeable, IRotatable


class Rotate(ICommand):
    def __init__(self, rotatable: IRotatable):
        self.r = rotatable

    def execute(self):
        self.r.set_direction(
            (self.r.get_direction() + self.r.get_angular_velocity()) % self.r.get_directions_number()
        )


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
