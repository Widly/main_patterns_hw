from typing import Type

from features.base.interfaces import ICommand


class ExceptionHandler:
    def __init__(self):
        self.rules = {}

    def setup(self, cmd: Type[ICommand], exc: Type[Exception] | None, action):
        """
        Создать правило для обработчика ошибок.
        :param cmd: тип команды
        :param exc: тип исключения или None для произвольного исключения
        :param action: действие которое необходимо выполнить в случае соответствия
        :return:
        """
        self.rules[(cmd, exc)] = action

    def handle(self, cmd: ICommand, exc: Exception):
        """
        Обработать исключение для команды.
        В случае если правило для переданной пары (команда + исключение) существует правило - вызывается действие
         определенное для этого правила. Иначе вызывается переданное исключение.
        :param cmd: экземпляр команды
        :param exc: экземпляр исключения
        :return:
        """
        action = self.rules.get((cmd.__class__, exc.__class__))
        if not action:
            # Пытаемся найти правило для произвольного исключения
            action = self.rules.get((cmd.__class__, None))

        if action:
            action(cmd, exc)
        else:
            raise exc
