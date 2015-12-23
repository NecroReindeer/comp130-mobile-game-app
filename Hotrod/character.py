"""This module includes classes for the enemies and player.

Classes:
Character(Widget) -- class that all characters inherit from
EnemyBeetle(Character) -- class that all enemies inherit from
PlayerBeetle(Character) -- class for the player beetle
RedBeetle(EnemyBeetle) -- class for the red beetle enemy
PinkBeetle(EnemyBeetle) -- class for the pink beetle enemy
BlueBeetle(EnemyBeetle) -- class for the blue beetle enemy
OrangeBeetle(EnemyBeetle) -- class for the orange beetle enemy
"""

from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.properties import NumericProperty
from kivy.properties import ReferenceListProperty
from kivy.properties import BooleanProperty
from kivy.vector import Vector
from kivy.clock import Clock

import direction
import level_cell
import test

class Character(Widget):
    """Class that characters inherit from.

    Public methods:
    move() -- move the character. Should be called every frame.
    initialise(start_position) -- set up the size and position of the character
    update_character() -- ensure that the size and position is correct
    """
    # Give characters access to other widgets through game widget
    game = ObjectProperty(None)

    # All characters have the following properties
    x_position = NumericProperty(0)
    y_position = NumericProperty(0)
    grid_position = ReferenceListProperty(x_position, y_position)

    speed = NumericProperty(0)
    speed_multiplier = NumericProperty(1)
    color = ObjectProperty((0, 0, 0))

    current_direction = ObjectProperty(direction.Direction.right)
    next_direction = ObjectProperty(direction.Direction.right)

    def move(self):
        if isinstance(self, EnemyBeetle):
            self._set_next_direction()
        # Copy of previous window position
        previous_pos = self.center[:]
        self.pos = Vector(self.current_direction.value[0] * self.speed,
                          self.current_direction.value[1] * self.speed) + self.pos
        self._check_position()
        self._update_direction((previous_pos))
        self._update_position()

    def initialise(self, start_position):
        self.grid_position = start_position
        starting_cell = self.game.level.get_cell(start_position)
        # Set size to interior cell size
        self.size = starting_cell.interior
        self.center = starting_cell.center

    def update_character(self):
        """Update the character's size and position relative to the level"""
        # So that size and position is correct if window size changes
        current_cell = self.game.level.get_cell(self.grid_position)
        self.center = current_cell.center
        self.size = current_cell.interior

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
        grid_position = self.game.level.convert_to_grid_position(self.center)
        self.grid_position = grid_position


class PlayerBeetle(Character):
    """Class for the player character. All methods used are in Character."""
    color = ObjectProperty((1, 1, 0))
    dead = BooleanProperty(False)

    def on_grid_position(self, instance, value):
        """Kivy event called when grid position changes. Check if player has
        collided with an enemy on player position change"""
        for enemy in self.game.enemies:
            if enemy.grid_position == self.grid_position:
                self.dead = True

    def on_dead(self, instance, value):
        """Kivy event called when player is set to dead. Take off a life and
        resets player status to alive."""
        if self.dead:
             self.game.lives -= 1
             self.dead = False
        else:
            pass


class EnemyBeetle(Character):
    """Class for enemy characters.

    Kivy Properties:
    pursuing -- bool that indicates which mode the enemy is in
    mode_change_timer -- the number of seconds the next mode change will
                         scheduled for
    """
    pursuing = BooleanProperty(True)
    mode_change_timer = NumericProperty(10)

    def _set_next_direction(self):
        """Set the next direction"""
        self.target_position = self.get_target_position()
        possible_moves = self.__get_possible_moves(self.current_direction)
        best_move = self.__get_shortest_move(possible_moves)
        self.next_direction = best_move

    def __get_possible_moves(self, current_direction):
        """Return the a list of directions the enemy is allowed to move in.

        Arguments:
        current_direction -- current direction of travel travelling in as direction.Direction
        """
        # List in this order means priority is up-left-down-right when using directions.pop
        directions = [direction.Direction.right,
                      direction.Direction.down,
                      direction.Direction.left,
                      direction.Direction.up]
        possible_directions = [dir for dir in directions if self.__direction_is_allowed(dir)]
        return possible_directions

    def __get_shortest_move(self, possible_moves):
        """Return the direction that results in being in the cell nearest the
        target cell as direction.Direction.

        Arguments:
        possible_moves -- list of directions the enemy is allowed to travel in
        """
        current_cell = self.game.level.get_cell(self.grid_position)
        best_moves = []
        shortest_distance = None
        for move in possible_moves:
            adjacent_cell = self.game.level.get_adjacent_cell(current_cell, move)
            adjacent_cell_coordinates = adjacent_cell.coordinates
            distance = Vector(adjacent_cell_coordinates).distance(self.target_position)

            if distance <= shortest_distance or shortest_distance == None:
                # This ensures that distances are added in both distance order and
                # priority order (since possible_moves is in priority order)
                shortest_distance = distance
                best_moves.append(move)
        # Return the shortest move that is the highest priority in up-left-down-right
        return best_moves.pop()

    def __direction_is_allowed(self, direction):
        """Return true if the enemy is allowed to travel in the given direction,
        else return false.

        Arguments:
        direction -- direction to be checked as direction.Direction
        """
        current_cell = self.game.level.get_cell(self.grid_position)
        # Cannot move in the direction if it reverses current direction or if there is a wall
        if current_cell.get_edge(direction).type == level_cell.CellEdgeType.wall:
            return False
        elif direction == self.current_direction.get_opposite():
            return False
        else:
            return True

    def change_mode(self, dt):
        """Switch the mode between scatter and chase mode and reverse direction"""
        self.pursuing = not self.pursuing
        self.current_direction = self.current_direction.get_opposite()

        if self.pursuing:
            self.mode_change_timer = 10
            Clock.schedule_once(self.change_mode, self.mode_change_timer)
        else:
            self.mode_change_timer = 5
            Clock.schedule_once(self.change_mode, self.mode_change_timer)

    def on_grid_position(self, instance, value):
        """Kivy event called when grid position changes. Check if enemy has
        collided with player on enemy position change"""
        if self.game.player.grid_position == self.grid_position:
            self.game.player.dead = True


class RedBeetle(EnemyBeetle):
    color = ObjectProperty((1, 0, 0))

    def get_target_position(self):
        """Determine and return the target position"""
        if self.pursuing:
            # For testing purposes
            self.target.pos = self.game.level.convert_to_window_position(self.game.player.grid_position)
            # Target position is always player's position
            return self.game.player.grid_position
        else:
            # Upper right corner
            target_position = (self.game.level.columns + 1, self.game.level.rows + 1)
            self.target.pos = self.game.level.convert_to_window_position(target_position)
            return target_position


class PinkBeetle(EnemyBeetle):
    color = ObjectProperty((1, 0, 1))

    def get_target_position(self):
        """Determine and return the target position"""
        if self.pursuing:
            player_position = self.game.player.grid_position
            player_direction_vector = self.game.player.current_direction.value
            # Target position is the 2 cells ahead of the player
            target_position = Vector(player_position) + 2 * player_direction_vector
            # For testing purposes
            self.target.pos = self.game.level.convert_to_window_position(target_position)
            return target_position
        else:
            # Upper left corner
            target_position = (-1, self.game.level.rows + 1)
            self.target.pos = self.game.level.convert_to_window_position(target_position)
            return target_position

class BlueBeetle(EnemyBeetle):
    color = ObjectProperty((0, 1, 1))

    def get_target_position(self):
        """Determine and return the target position"""
        if self.pursuing:
            player_position = self.game.player.grid_position
            player_direction_vector = self.game.player.current_direction.value
            space_ahead_of_player = Vector(player_position) + 2 * player_direction_vector
            red_beetle_position = self.game.red_enemy.grid_position

            # Target position is double the vector between 2 spaces ahead of the
            # player and the red beetle
            target_position = 2 * Vector(space_ahead_of_player) - Vector(red_beetle_position)
            # For testing purposes
            self.target.pos = self.game.level.convert_to_window_position(target_position)
            return target_position
        else:
            # Bottom right
            target_position = (self.game.level.columns + 1, -1)
            self.target.pos = self.game.level.convert_to_window_position(target_position)
            return target_position


class OrangeBeetle(EnemyBeetle):
    color = ObjectProperty((1, 0.5, 0))

    def get_target_position(self):
        """Determine and return the target position"""
        if self.pursuing:
            player_position = self.game.player.grid_position
            distance_from_player = Vector(player_position).distance(self.grid_position)

            if distance_from_player > 4:
                # Target position is player if the player is more than 4 tiles away
                target_position = player_position
            else:
                # Target position is bottom left corner if player is within 4 tiles
                target_position = -1, -1
            # For testing purposes
            self.target.pos = self.game.level.convert_to_window_position(target_position)
            return target_position
        else:
            # Bottom left
            target_position = (-1, -1)
            self.target.pos = self.game.level.convert_to_window_position(target_position)
            return target_position








