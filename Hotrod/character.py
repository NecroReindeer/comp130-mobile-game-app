__author__ = 'Harriet'

from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty, ReferenceListProperty
from kivy.vector import Vector

import direction
import level_cell

class PlayerBeetle(Widget):
    # set starting grid position to 0, 0
    x_position = NumericProperty(0)
    y_position = NumericProperty(0)
    grid_position = ReferenceListProperty(x_position, y_position)

    speed = NumericProperty(0)
    color = ObjectProperty((1, 0, 1))

    current_direction = ObjectProperty(direction.Direction.right)
    next_direction = ObjectProperty(direction.Direction.right)

    def check_position(self):
        """Move the player to the center of the current cell if it
        tries to move through a wall
        """
        current_cell = self.parent.level.cells[self.x_position][self.y_position]
        current_edge = current_cell.get_edge(self.current_direction)
        if current_edge.type == level_cell.CellEdgeType.wall:
            if self.current_direction == direction.Direction.right:
                if self.center_x > current_cell.center_x:
                    self.center_x = current_cell.center_x

            elif self.current_direction == direction.Direction.left:
                if self.center_x < current_cell.center_x:
                    self.center_x = current_cell.center_x

            elif self.current_direction == direction.Direction.up:
                if self.center_y > current_cell.center_y:
                    self.center_y = current_cell.center_y

            elif self.current_direction == direction.Direction.down:
                if self.center_y < current_cell.center_y:
                    self.center_y = current_cell.center_y

    def update_direction(self, (previous_x, previous_y)):
        """Check if there is a pending movement direction and execute it
        if possible
        """
        if self.next_direction != self.current_direction:
            current_cell = self.parent.level.cells[self.x_position][self.y_position]
            current_edge = current_cell.get_edge(self.next_direction)

            if current_edge.type == level_cell.CellEdgeType.passage:
                if self.current_direction == direction.Direction.right:
                    # Set new direction for next frame if player has moved into/past center or is at the center of cell
                    if ((self.center_x >= current_cell.center_x and current_cell.center_x > previous_x)or
                            (self.center_x == current_cell.center_x and previous_x == current_cell.center_x)):
                        self.center_x = current_cell.center_x
                        self.set_direction()

                elif self.current_direction == direction.Direction.left:
                    if ((self.center_x <= current_cell.center_x and current_cell.center_x < previous_x) or
                            (self.center_x == current_cell.center_x and previous_x == current_cell.center_x)):
                        self.center_x = current_cell.center_x
                        self.set_direction()

                elif self.current_direction == direction.Direction.up:
                    if ((self.center_y >= current_cell.center_y and current_cell.center_y > previous_y) or
                            (self.center_y == current_cell.center_y and previous_y == current_cell.center_y)):
                        self.center_y = current_cell.center_y
                        self.set_direction()

                elif self.current_direction == direction.Direction.down:
                    if ((self.center_y <= current_cell.center_y and current_cell.center_y < previous_y) or
                            (self.center_y == current_cell.center_y and previous_y == current_cell.center_y)):
                        self.center_y = current_cell.center_y
                        self.set_direction()

    def set_direction(self):
        self.current_direction = self.next_direction

    def update_position(self):
        """Updates the stored position of the player in grid coordinates"""
        grid_x = int((self.center_x - self.parent.level.padding) / self.parent.level.cell_size[0])
        grid_y = int(self.center_y / self.parent.level.cell_size[1])
        self.grid_position = grid_x, grid_y

    def move(self):
        # Copy of previous window position
        previous_pos = self.center[:]
        self.pos = Vector(self.current_direction.value[0] * self.speed,
                          self.current_direction.value[1] * self.speed) + self.pos
        self.check_position()
        self.update_direction((previous_pos))
        self.update_position()
