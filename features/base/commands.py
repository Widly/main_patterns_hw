import inspect
from typing import Iterable

from exceptions import CommandException
from iocs import IoC
from .interfaces import ICommand, UObject


class MacroCommand(ICommand):
    def __init__(self, commands: Iterable[ICommand]):
        self.commands = commands

    def execute(self) -> None:
        try:
            for cmd in self.commands:
                cmd.execute()
        except Exception as e:
            raise CommandException(e)


class GetProperty(ICommand):
    def __init__(self, obj: UObject, key: str):
        self.obj = obj
        self.key = key

    def execute(self) -> object:
        return self.obj.get_property(self.key)


class SetProperty(ICommand):
    def __init__(self, obj: UObject, key: str, value: object):
        self.obj = obj
        self.key = key
        self.value = value

    def execute(self) -> None:
        self.obj.set_property(self.key, self.value)


class LambdaCommand(ICommand):
    def __init__(self, action):
        self.action = action

    def execute(self) -> None:
        self.action()


class CreateAdapterException(Exception):
    pass


class InitCreateCommandAdapterStrategy(ICommand):
    """
    Данная команда регистрирует в IoC стратегию которая:
        1. Генерирует адаптер для произвольного интерфейса
        2. Оборачивает переданный игровой объект в этот адаптер

    Адаптер позволяет позволяет взаимодействовать с игровыми объектами не напрямую, а через IoC, благодаря чему
    возможно переопределять логику взаимодействия с объектами на лету.

    Например, для следующего интерфейса:

        class IActionable:
            def get_field_1(self):
                ...

            def set_field_1(self, value):
                ...

            def get_field_2(self):
                ...

    В результате вызова:
        IoC.resolve("Adapter", IActionable, obj)

    Будет сгенерирован следующий адаптер:

        class IActionableAdapter(IActionable):
            def __init__(self, obj: UObject):
                self.obj = obj

            def get_field_1(self):
                return IoC.resolve('IActionable:field_1.get', self.obj)

            def set_field_1(self, value):
                IoC.resolve('IActionable:field_1.set', self.obj, new_v).execute()

            def get_field_2(self):
                return IoC.resolve('IActionable:field_2.get', self.obj)
    """

    adapters = {}  # Ранее созданные адаптеры

    def function_factory(self, interface, f_name):
        """Создает метод для генерируемого класса адаптера"""
        op_type, property_name = f_name.split('_', 1)
        ioc_path = f'{interface.__name__}:{property_name}.{op_type}'

        if op_type == 'set':
            def new_f(self, *args, **kwargs):
                IoC.resolve(ioc_path, self.obj, *args, **kwargs).execute()
        elif op_type == 'get':
            def new_f(self, *args, **kwargs):
                return IoC.resolve(ioc_path, self.obj, *args, **kwargs)
        else:
            raise CreateAdapterException(f"'{op_type}' is not allowd operation type!")

        return new_f

    def create_adapter(self, interface):
        """Создание адаптера"""
        if interface in self.adapters:
            # Пользуемся адаптерами созданными ранее
            return self.adapters[interface]

        def constructor(self, obj):
            self.obj = obj

        class_methods = {
            '__init__': constructor
        }

        for f_name, f in inspect.getmembers(interface, predicate=inspect.isfunction):
            class_methods[f_name] = self.function_factory(interface, f_name)

        adapter = type(f'{interface.__name__}Adapter', (interface,), class_methods)
        self.adapters[interface] = adapter

        return adapter

    def execute(self) -> None:
        IoC.resolve(
            'IoC.Register',
            'Adapter',
            lambda interface, obj: self.create_adapter(interface)(obj)
        ).execute()
