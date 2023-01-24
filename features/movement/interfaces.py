from abc import ABC, abstractmethod

import numpy as np

from features.base.interfaces import UObject


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


class IFuelable(ABC):
    @abstractmethod
    def get_fuel_level(self) -> int:
        ...

    @abstractmethod
    def set_fuel_level(self, new_fuel_level: int) -> None:
        ...

    @abstractmethod
    def get_fuel_consumption(self) -> int:
        ...


class IMovementStartable(ABC):
    @abstractmethod
    def set_velocity(self, v: np.array) -> None:
        ...

    def get_object(self) -> UObject:
        ...
