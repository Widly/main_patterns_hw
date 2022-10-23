from abc import ABC, abstractmethod


class IRotatable(ABC):
    @abstractmethod
    def get_direction(self) -> int:
        ...

    @abstractmethod
    def get_angular_velocity(self) -> int:
        ...

    @abstractmethod
    def set_direction(self, new_d: int) -> None:
        ...

    @abstractmethod
    def get_directions_number(self) -> int:
        pass


class Rotate:
    def __init__(self, rotatable: IRotatable):
        self.r = rotatable

    def execute(self):
        self.r.set_direction(
            (self.r.get_direction() + self.r.get_angular_velocity()) % self.r.get_directions_number()
        )
