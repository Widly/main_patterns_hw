from unittest import TestCase
from unittest.mock import Mock

from commands import Rotate
from interfaces import IRotatable


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
