import numpy as np

from features.base.commands import LambdaCommand
from features.base.interfaces import ICommand, UObject
from iocs import IoC


class GameObject(UObject):
    def __init__(self):
        self.storage = {}

    def get_property(self, key: str) -> object:
        return self.storage[key]

    def set_property(self, key: str, value: object) -> None:
        self.storage[key] = value


class GameRepeatedCommand(ICommand):
    def __init__(self, cmd):
        self.cmd = cmd

    def execute(self) -> None:
        self.cmd.execute()
        IoC.resolve('Queue.Put', self).execute()


class InterpretGameCommand(ICommand):
    def __init__(self, game_id, operation):
        self.game_id = game_id
        self.operation = operation

    def execute(self) -> None:
        IoC.resolve('Scopes.Current.Set', self.game_id).execute()
        game_obj = IoC.resolve('Objects.Get', self.operation.pop('object_id'))
        operation_name = self.operation.pop('name')

        operation = IoC.resolve(f'Operations.{operation_name}', game_obj, **self.operation)
        IoC.resolve('Queue.Put', operation).execute()


class GameCommand(ICommand):
    def __init__(self, game_id):
        self.game_id = game_id
        self.queue = []

        IoC.resolve('Scopes.New', game_id)
        IoC.resolve('Scopes.Current.Set', game_id).execute()

        IoC.resolve(
            'IoC.Register',
            'Queue.Put',
            lambda cmd: LambdaCommand(lambda: self.queue.append(cmd))
        ).execute()

        IoC.resolve(
            'IoC.Register',
            'Queue.PutWithRepeat',
            lambda cmd: IoC.resolve('Queue.Put', GameRepeatedCommand(cmd))
        ).execute()

        game_objects = {}

        IoC.resolve(
            'IoC.Register',
            'Objects.Add',
            lambda obj_id, obj: LambdaCommand(lambda: game_objects.update({obj_id: obj}))
        ).execute()

        IoC.resolve(
            'IoC.Register',
            'Objects.Get',
            lambda obj_id: game_objects[obj_id]
        ).execute()

        IoC.resolve(
            'IoC.Register',
            'Objects.All',
            lambda: game_objects.values()
        ).execute()

        obj1 = GameObject()
        obj1_id = 'obj-1'
        obj1.set_property('id', obj1_id)
        obj1.set_property('position', np.array([0, 0]))
        obj1.set_property('fuel_level', 100)
        obj1.set_property('directions_number', 4)
        obj1.set_property('direction', 1)
        obj1.set_property('angular_velocity', 1)
        obj1.set_property('fuel_consumption', 1)
        IoC.resolve('Objects.Add', obj1_id, obj1).execute()

        obj2 = GameObject()
        obj2_id = 'obj-2'
        obj2.set_property('id', obj2_id)
        obj2.set_property('position', np.array([0, 1000]))
        obj2.set_property('fuel_level', 100)
        obj2.set_property('directions_number', 4)
        obj2.set_property('direction', 3)
        obj2.set_property('angular_velocity', 1)
        obj2.set_property('fuel_consumption', 1)
        IoC.resolve('Objects.Add', obj2_id, obj2).execute()

    def execute(self) -> None:
        IoC.resolve('Scopes.Current.Set', self.game_id).execute()

        print(f'Game : {self.game_id}')
        for obj in IoC.resolve('Objects.All'):
            print('\t', f'{obj.get_property("id")}:')
            print('\t\t', f'position: {obj.get_property("position")}')
            print('\t\t', f'fuel_level: {obj.get_property("fuel_level")}')
            print('\t\t', f'fuel_consumption: {obj.get_property("fuel_consumption")}')
            print('\t\t', f'direction: {obj.get_property("direction")}')
            print('\t\t', f'directions_number: {obj.get_property("directions_number")}')
            print('\t\t', f'angular_velocity: {obj.get_property("angular_velocity")}')
        print()

        try:
            cmd = self.queue.pop(0)
        except IndexError:
            return

        cmd.execute()


class CreateGameCommand(ICommand):
    id_counter = 1

    def execute(self) -> None:
        game_id = f'game-{self.id_counter}'
        CreateGameCommand.id_counter += 1

        game_cmd = GameCommand(game_id)

        # Команда кладет в очередь сама себя
        IoC.resolve('Thread.PutWithRepeat', game_cmd).execute()


class UserActionsPlugin(ICommand):
    def execute(self) -> None:
        IoC.resolve(
            'IoC.Register',
            'UserActions.CreateGame',
            lambda: CreateGameCommand()
        ).execute()

        IoC.resolve(
            'IoC.Register',
            'UserActions.InterpretGameCommand',
            lambda game_id, operation: InterpretGameCommand(game_id, operation)
        ).execute()


