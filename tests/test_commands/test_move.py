from unittest import TestCase
from unittest.mock import Mock

import numpy as np

from features.movement.commands import Move
from features.movement.interfaces import IMovable


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
