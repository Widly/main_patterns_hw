from abc import ABC, abstractmethod

import numpy as np


class ICommand(ABC):
    @abstractmethod
    def execute(self) -> None:
        ...


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
