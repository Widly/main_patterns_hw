from abc import ABC, abstractmethod


class ICommand(ABC):
    @abstractmethod
    def execute(self) -> None:
        ...


class UObject(ABC):
    @abstractmethod
    def get_property(self, key: str) -> object:
        ...

    @abstractmethod
    def set_property(self, key: str, value: object) -> None:
        ...
