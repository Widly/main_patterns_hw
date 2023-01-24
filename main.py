import json
import socket
from time import sleep

from exception_handler import ExceptionHandler
from features.base.builders import OperationBuilder
from features.base.commands import InitCreateCommandAdapterStrategy, MacroCommand, LambdaCommand
from features.movement.commands import MoveCommandPluginCommand, FuelCommandsPluginCommand
from features.rotation.commands import RotateCommandsPluginCommand
from game.commands import UserActionsPlugin
from iocs import IoC
from iocs.scope_based_strategy import InitScopesCommand
from thread.commands import StartThreadCommandPlugin


HOST = "127.0.0.1"
PORT = 12345


def listen_socket():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        while True:
            conn, addr = s.accept()
            data = conn.recv(1024)

            action_data = json.loads(data.decode('utf-8'))
            action_name = action_data.pop("name")
            action = IoC.resolve(f'UserActions.{action_name}', **action_data)
            IoC.resolve("Thread.Put", action).execute()

            conn.close()


if __name__ == '__main__':
    InitScopesCommand().execute()
    InitCreateCommandAdapterStrategy().execute()
    MoveCommandPluginCommand().execute()
    FuelCommandsPluginCommand().execute()
    RotateCommandsPluginCommand().execute()
    StartThreadCommandPlugin().execute()
    UserActionsPlugin().execute()

    exc_handler = ExceptionHandler()
    IoC.resolve('IoC.Register', 'ExceptionHandler', lambda: exc_handler).execute()

    # Правила игры
    IoC.resolve(
        'IoC.Register',
        'Operations.Movement.Description',
        lambda: [
            'Commands.CheckFuel',
            'Commands.Move',
            'Commands.BurnFuel'
        ]
    ).execute()

    IoC.resolve(
        'IoC.Register',
        'Operations.Rotation.Description',
        lambda: [
            'Commands.Rotate',
            'Commands.ChangeVelocity'
        ]
    ).execute()

    IoC.resolve(
        'IoC.Register',
        'Operations.Movement',
        OperationBuilder('Operations.Movement').build
    ).execute()

    IoC.resolve(
        'IoC.Register',
        'Operations.Rotation',
        OperationBuilder('Operations.Rotation').build
    ).execute()

    IoC.resolve(
        'IoC.Register',
        'Operations.StartMovement',
        lambda obj, *args, **kwargs: IoC.resolve('Commands.StartMovement', obj, *args, **kwargs)
    ).execute()

    thread_id = 'thread-id'
    IoC.resolve("Thread.Start", thread_id).execute()
    IoC.resolve('Scopes.Current.Set', thread_id).execute()

    IoC.resolve(
        "Thread.PutWithRepeat",
        MacroCommand([
            LambdaCommand(lambda: print('-----------------')),
            LambdaCommand(lambda: sleep(2))
        ])
    ).execute()

    listen_socket()

    thread = IoC.resolve("Thread")
    # IoC.resolve("Thread.Put", IoC.resolve("Thread.SoftStop")).execute()
    thread.join()
