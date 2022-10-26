from unittest import TestCase
from unittest.mock import Mock

import numpy as np

from commands import Move, Rotate
from interfaces import IMovable, IRotatable


class TestMove(TestCase):
    def setUp(self) -> None:
        movable = Mock(IMovable)
        movable.get_position.return_value = np.array([12, 5])
        movable.get_velocity.return_value = np.array([-7, 3])

        self.movable = movable

    def test_move(self):
        move = Move(self.movable)
        move.execute()

        # Не могу воспользоваться assert_called_with: self.movable.set_position.assert_called_with(np.array([5, 8]))
        # поскольку np.array нельзя сравнивать через ==
        np.testing.assert_array_equal(np.array([5, 8]), self.movable.set_position.call_args[0][0])
        self.assertEqual(1, len(self.movable.set_position.call_args[0]))

    def test_get_position_error(self):
        self.movable.get_position.side_effect = Exception('Error get position')
        move = Move(self.movable)

        with self.assertRaisesRegex(Exception, 'Error get position'):
            move.execute()

    def test_get_velocity_error(self):
        self.movable.get_velocity.side_effect = Exception('Error get velocity')
        move = Move(self.movable)

        with self.assertRaisesRegex(Exception, 'Error get velocity'):
            move.execute()

    def test_set_position_error(self):
        self.movable.set_position.side_effect = Exception('Error set position')

        move = Move(self.movable)
        with self.assertRaisesRegex(Exception, 'Error set position'):
            move.execute()


class TestRotate(TestCase):
    def setUp(self) -> None:
        rotatable = Mock(IRotatable)
        rotatable.get_direction.return_value = 13
        rotatable.get_angular_velocity.return_value = 5
        rotatable.get_directions_number.return_value = 16
        self.rotatable = rotatable

    def test_rotate(self):
        rotate = Rotate(self.rotatable)
        rotate.execute()

        self.rotatable.set_direction.assert_called_with(2)

    def test_get_direction_error(self):
        self.rotatable.get_direction.side_effect = Exception('Error get direction')
        rotate = Rotate(self.rotatable)

        with self.assertRaisesRegex(Exception, 'Error get direction'):
            rotate.execute()

    def test_get_angular_velocity_error(self):
        self.rotatable.get_angular_velocity.side_effect = Exception('Error get angular velocity')
        rotate = Rotate(self.rotatable)

        with self.assertRaisesRegex(Exception, 'Error get angular velocity'):
            rotate.execute()

    def test_get_directions_number_error(self):
        self.rotatable.get_direction.side_effect = Exception('Error get directions number')
        rotate = Rotate(self.rotatable)

        with self.assertRaisesRegex(Exception, 'Error get directions number'):
            rotate.execute()

    def test_set_direction_error(self):
        self.rotatable.set_direction.side_effect = Exception('Error set direction')
        rotate = Rotate(self.rotatable)

        with self.assertRaisesRegex(Exception, 'Error set direction'):
            rotate.execute()
