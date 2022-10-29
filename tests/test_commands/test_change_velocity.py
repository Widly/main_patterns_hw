from unittest import TestCase
from unittest.mock import Mock

import numpy as np

from commands import ChangeVelocity
from interfaces import IVelocityChangeable


class TestChangeVelocity(TestCase):
    def test_command(self):
        """Тестируем логику изменения направления вектора скорости в зависимости от текущего угла поворота"""
        obj = Mock(IVelocityChangeable)
        obj.get_velocity.return_value = np.array([4, 6])
        obj.get_angle.return_value = 2.5  # Радианы

        cmd = ChangeVelocity(obj)
        cmd.execute()

        # Как вычисляется новый вектор
        # velocity_modulus = sqrt(4**2 + 6**2) = 7.2111
        # new_x = 7.2111 * cos(2.5) = 7.2111 * -0.801 = -5.7760911
        # new_y = 7.2111 * sin(2.5) = 7.2111 * 0.598 = 4.312
        # Округление приводит к результату [-6, 4]

        np.testing.assert_array_equal(np.array([-6, 4]), obj.set_velocity.call_args[0][0])
        self.assertEqual(1, len(obj.set_velocity.call_args[0]))

    def test_get_velocity_error(self):
        """Тестируем, что при невозможности прочитать скорость команда ничего не делает"""
        obj = Mock(IVelocityChangeable)
        obj.get_velocity.side_effect = Exception('Error get velocity')

        cmd = ChangeVelocity(obj)
        cmd.execute()
        obj.set_velocity.assert_not_called()
