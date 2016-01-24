"""Contain an enum to represent directions.

This module includes an enum for representing the directions left, down,
right and up.
"""

# Kivy modules
from kivy.vector import Vector

# Other modules
from enum import Enum


class Direction(Enum):
    """Store enumerations for directions.

    This is an enum to represent directions.
    Values are the vectors representing the direction.

    Public methods:
    get_angle -- return the angle corresponding to the direction
    get_opposite -- return the opposite direction
    """

    left = Vector(-1, 0)
    down = Vector(0, -1)
    right = Vector(1, 0)
    up = Vector(0, 1)

    def get_angle(self):
        """Return the rotation angle in degrees relevant to the Direction"""

        if self == Direction.left:
            return 0
        elif self == Direction.down:
            return 90
        elif self == Direction.right:
            return 180
        elif self == Direction.up:
            return 270

    def get_opposite(self):
        """Return the opposite Direction"""

        if self == Direction.left:
            return Direction.right
        elif self == Direction.down:
            return Direction.up
        elif self == Direction.right:
            return Direction.left
        elif self == Direction.up:
            return Direction.down
