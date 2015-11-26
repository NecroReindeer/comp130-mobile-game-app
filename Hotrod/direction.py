__author__ = 'Hat'


from enum import Enum

class Direction(Enum):
    right = (1, 0)
    down = (0, -1)
    left = (-1, 0)
    up = (0, 1)