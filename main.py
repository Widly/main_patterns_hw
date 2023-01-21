from time import sleep

from exception_handler import ExceptionHandler
from features.base.builders import OperationBuilder
from features.base.commands import InitCreateCommandAdapterStrategy, MacroCommand, LambdaCommand
from features.movement.commands import MoveCommandPluginCommand, FuelCommandsPluginCommand
from features.rotation.commands import RotateCommandsPluginCommand
from iocs import IoC
from iocs.scope_based_strategy import InitScopesCommand
from thread.commands import StartThreadCommandPlugin

if __name__ == '__main__':
    InitScopesCommand().execute()
    InitCreateCommandAdapterStrategy().execute()
    MoveCommandPluginCommand().execute()
    FuelCommandsPluginCommand().execute()
    RotateCommandsPluginCommand().execute()
    StartThreadCommandPlugin().execute()

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

    thread_id = 'thread-id'
    IoC.resolve("Thread.Start", thread_id).execute()
    IoC.resolve('Scopes.Current.Set', thread_id).execute()

    IoC.resolve(
        "Thread.PutWithRepeat",
        MacroCommand([
            LambdaCommand(lambda: print('...')),
            LambdaCommand(lambda: sleep(1))
        ])
    ).execute()

    thread = IoC.resolve("Thread")
    # IoC.resolve("Thread.Put", IoC.resolve("Thread.SoftStop")).execute()
    thread.join()
