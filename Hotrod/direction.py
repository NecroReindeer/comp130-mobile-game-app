__author__ = 'Hat'


from enum import Enum

class Direction(Enum):
    left = (-1, 0)
    down = (0, -1)
    right = (1, 0)
    up = (0, 1)

    def get_angle(self):
        if self == Direction.left:
            return 0
        elif self == Direction.down:
            return 90
        elif self == Direction.right:
            return 180
        elif self == Direction.up:
            return 270

    def get_opposite(self):
        if self == Direction.left:
            return Direction.right
        elif self == Direction.down:
            return Direction.up
        elif self == Direction.right:
            return Direction.left
        elif self == Direction.up:
            return Direction.down
