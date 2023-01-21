from features.base.commands import MacroCommand
from features.base.interfaces import ICommand
from iocs import IoC

from random import randint


class CreateGameCommand(ICommand):
    def execute(self) -> None:
        game_id = f'game-{randint(1, 1000)}'
        print(game_id)

        game_cmd = GameCommand(game_id)

        # Команда кладет в очередь сама себя
        cmd = MacroCommand([
            game_cmd,
            IoC.resolve('Thread.Put', game_cmd)
        ])

        IoC.resolve('Thread.Put', cmd)


class GameCommand(ICommand):
    def __init__(self, game_id):
        self.game_id = game_id
        self.queue = []

        IoC.resolve('Scope.New', game_id)
        IoC.resolve('Scopes.Current.Set', game_id).execute()

        IoC.resolve(
            'IoC.Register',
            'Queue.Put',
            lambda cmd: self.queue.append(cmd)
        ).execute()

        # TODO Инициализация игры (через команду)
        # IoC.resolve(f'game.{game_id}').execute()

    def execute(self) -> None:
        IoC.resolve('Scopes.Current.Set', self.game_id).execute()

        try:
            cmd = self.queue.pop(0)
        except IndexError:
            return

        cmd.execute()
