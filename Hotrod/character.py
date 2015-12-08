__author__ = 'Harriet'

import random

from kivy.uix.widget import Widget
from kivy.properties import ListProperty
from kivy.properties import ObjectProperty
from kivy.properties import NumericProperty
from kivy.properties import ReferenceListProperty
from kivy.vector import Vector

import direction
import level_cell

class Character(Widget):
    game = ObjectProperty(None)

    # All characters have the following properties
    x_position = NumericProperty(0)
    y_position = NumericProperty(0)
    grid_position = ReferenceListProperty(x_position, y_position)

    speed = NumericProperty(0)
    color = ObjectProperty((0, 0, 0))

    current_direction = ObjectProperty(direction.Direction.right)
    next_direction = ObjectProperty(direction.Direction.right)


    def _check_position(self):
        """Move the player to the center of the current cell if it
        tries to move through a wall
        """
        current_cell = self.game.level.cells[self.x_position][self.y_position]
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

    def _update_direction(self, (previous_x, previous_y)):
        """Check if there is a pending movement direction and execute it
        if possible
        """
        if self.next_direction != self.current_direction:
            current_cell = self.game.level.cells[self.x_position][self.y_position]
            current_edge = current_cell.get_edge(self.next_direction)

            if current_edge.type == level_cell.CellEdgeType.passage:
                if self.current_direction == direction.Direction.right:
                    # Set new direction for next frame if player has moved into/past center or is at the center of cell
                    if ((self.center_x >= current_cell.center_x and current_cell.center_x > previous_x)or
                            (self.center_x == current_cell.center_x and previous_x == current_cell.center_x)):
                        self.center_x = current_cell.center_x
                        self._set_direction()

                elif self.current_direction == direction.Direction.left:
                    if ((self.center_x <= current_cell.center_x and current_cell.center_x < previous_x) or
                            (self.center_x == current_cell.center_x and previous_x == current_cell.center_x)):
                        self.center_x = current_cell.center_x
                        self._set_direction()

                elif self.current_direction == direction.Direction.up:
                    if ((self.center_y >= current_cell.center_y and current_cell.center_y > previous_y) or
                            (self.center_y == current_cell.center_y and previous_y == current_cell.center_y)):
                        self.center_y = current_cell.center_y
                        self._set_direction()

                elif self.current_direction == direction.Direction.down:
                    if ((self.center_y <= current_cell.center_y and current_cell.center_y < previous_y) or
                            (self.center_y == current_cell.center_y and previous_y == current_cell.center_y)):
                        self.center_y = current_cell.center_y
                        self._set_direction()

    def _set_direction(self):
        self.current_direction = self.next_direction

    def _update_position(self):
        """Updates the stored position of the player in grid coordinates"""
        grid_x = int((self.center_x - self.game.level.padding) / self.game.level.cell_size[0])
        grid_y = int(self.center_y / self.game.level.cell_size[1])
        self.grid_position = grid_x, grid_y

    def move(self):
        # Copy of previous window position
        previous_pos = self.center[:]
        self.pos = Vector(self.current_direction.value[0] * self.speed,
                          self.current_direction.value[1] * self.speed) + self.pos
        self._check_position()
        self._update_direction((previous_pos))
        self._update_position()


class EnemyBeetle(Character):
    target_position = ObjectProperty(None)

    def move(self):
        # Copy of previous window position
        self.set_next_direction()
        previous_pos = self.center[:]
        self.pos = Vector(self.current_direction.value[0] * self.speed,
                          self.current_direction.value[1] * self.speed) + self.pos
        self._check_position()
        self._update_direction((previous_pos))
        self._update_position()

    def direction_is_allowed(self, direction):
        current_cell = self.game.level.get_cell(self.grid_position)
        # Cannot move in the direction if it reverses current direction or if there is a wall
        if current_cell.get_edge(direction).type == level_cell.CellEdgeType.wall:
            return False
        elif direction == self.current_direction.get_opposite():
            return False
        else:
            return True

    def get_possible_moves(self, current_direction):
        directions = [direction.Direction.right,
                      direction.Direction.down,
                      direction.Direction.left,
                      direction.Direction.up]
        possible_directions = [dir for dir in directions if self.direction_is_allowed(dir)]
        return possible_directions


    def get_shortest_move(self, possible_moves):
        current_cell = self.game.level.get_cell(self.grid_position)
        shortest_distance = None
        best_move = None
        for move in possible_moves:
            adjacent_cell = self.game.level.get_adjacent_cell(current_cell, move)
            adjacent_cell_coordinates = adjacent_cell.coordinates
            distance = Vector(adjacent_cell_coordinates).distance(self.target_position)
            if distance < shortest_distance or shortest_distance == None:
                shortest_distance = distance
                best_move = move
            elif distance == shortest_distance:
                # Choose randomly if both are equal distance
                best_move = random.choice((move, best_move))
        return best_move

    def set_next_direction(self):
        self.target_position = self.get_target_position()
        possible_moves = self.get_possible_moves(self.current_direction)
        best_move = self.get_shortest_move(possible_moves)
        self.next_direction = best_move


class RedBeetle(EnemyBeetle):
    color = ObjectProperty((1, 0, 0))

    def get_target_position(self):
        return self.game.player.grid_position



class PinkBeetle(EnemyBeetle):
    color = ObjectProperty((1, 0, 1))

    def get_target_position(self):
        player_position = self.game.player.grid_position
        player_direction = self.game.player.current_direction



class PlayerBeetle(Character):
    color = ObjectProperty((1, 1, 0))





