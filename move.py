from abc import ABC, abstractmethod

import numpy as np


class IMovable(ABC):
    @abstractmethod
    def get_position(self) -> np.array:
        ...

    @abstractmethod
    def get_velocity(self) -> np.array:
        ...

    @abstractmethod
    def set_position(self, new_v: np.array) -> None:
        ...


class Move:
    def __init__(self, movable: IMovable):
        self.m = movable

    def execute(self):
        self.m.set_position(self.m.get_position() + self.m.get_velocity())
