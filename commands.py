from interfaces import IMovable, IRotatable


class Move:
    def __init__(self, movable: IMovable):
        self.m = movable

    def execute(self):
        self.m.set_position(self.m.get_position() + self.m.get_velocity())


class Rotate:
    def __init__(self, rotatable: IRotatable):
        self.r = rotatable

    def execute(self):
        self.r.set_direction(
            (self.r.get_direction() + self.r.get_angular_velocity()) % self.r.get_directions_number()
        )
