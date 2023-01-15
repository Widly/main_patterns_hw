from unittest import TestCase
from unittest.mock import Mock

from features.movement.commands import CheckFuel, BurnFuel
from exceptions import CommandException
from features.movement.interfaces import IFuelable


class TestCheckFuel(TestCase):
    def test_command(self):
        """Тестируем, что команда корректно отрабатывает при достаточном количестве топлива"""
        fuelable = Mock(IFuelable)
        fuelable.get_fuel_level.return_value = 6
        fuelable.get_fuel_consumption.return_value = 4

        cmd = CheckFuel(fuelable)
        cmd.execute()

    def test_check_fuel_error(self):
        """Тестируем, что команда вызывает ошибку при недостаточном количестве топлива"""
        fuelable = Mock(IFuelable)
        fuelable.get_fuel_level.return_value = 6
        fuelable.get_fuel_consumption.return_value = 7

        cmd = CheckFuel(fuelable)
        with self.assertRaisesRegex(CommandException, 'Not enough fuel'):
            cmd.execute()


class TestBurnFuel(TestCase):
    def test_command(self):
        """Тестируем сжигание топлива"""
        fuelable = Mock(IFuelable)
        fuelable.get_fuel_level.return_value = 6
        fuelable.get_fuel_consumption.return_value = 4

        cmd = BurnFuel(fuelable)
        cmd.execute()
        fuelable.set_fuel_level.assert_called_with(2)
