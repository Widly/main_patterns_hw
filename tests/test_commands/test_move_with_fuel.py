from unittest import TestCase
from unittest.mock import Mock

import numpy as np

from commands import MoveWithFuel
from exceptions import CommandException
from interfaces import IFuelable, IMovable


class TestMoveWithFuel(TestCase):
    def setUp(self) -> None:
        class UObject(IMovable, IFuelable):
            ...

        obj = Mock(UObject)
        obj.get_fuel_level.return_value = 6
        obj.get_fuel_consumption.return_value = 4
        obj.get_position.return_value = np.array([12, 5])
        obj.get_velocity.return_value = np.array([-7, 3])

        self.obj = obj
        self.command = MoveWithFuel(obj)

    def test_command(self):
        """Тестируем корректность работы команды"""
        self.command.execute()

        # Произошло движение объекта
        np.testing.assert_array_equal(np.array([5, 8]), self.obj.set_position.call_args[0][0])
        self.assertEqual(1, len(self.obj.set_position.call_args[0]))

        # Произошло сжигание топлива
        self.obj.set_fuel_level.assert_called_with(2)

    def test_not_enough_fuel(self):
        """Тестируем, что при недостатке топлива движение не происходит и топливо не сжигается"""
        self.obj.get_fuel_level.return_value = 3

        with self.assertRaisesRegex(CommandException, 'Not enough fuel'):
            self.command.execute()

        # Позиция объекта не изменилась, сжигание топлива не произошло
        self.obj.set_position.assert_not_called()
        self.obj.set_fuel_level.assert_not_called()
