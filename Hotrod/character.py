"""Store classes relating to in-game characters.

This module includes classes for the enemies and player character.

Classes:
Character(Widget) -- class that all characters inherit from
EnemyBeetle(Character) -- class that all enemies inherit from
PlayerBeetle(Character) -- class for the player beetle
RedBeetle(EnemyBeetle) -- class for the red beetle enemy
PinkBeetle(EnemyBeetle) -- class for the pink beetle enemy
BlueBeetle(EnemyBeetle) -- class for the blue beetle enemy
OrangeBeetle(EnemyBeetle) -- class for the orange beetle enemy
"""

import random

from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.properties import NumericProperty
from kivy.properties import ReferenceListProperty
from kivy.properties import BooleanProperty
from kivy.core.audio import SoundLoader
from kivy.vector import Vector
from kivy.clock import Clock

import collectable
import direction
import level_cell
import test

class Character(Widget):

    """Store methods and properties relevant to all characters.

    All characters inherit from this class. It includes methods that
    are universal to all characters, such as those managing movement.

    Public methods:
    move() -- move the character. Should be called every frame.
    initialise(start_position) -- set up the size and position of the character
    update_character() -- ensure that the size and position is correct
    """

    # Give characters access to other widgets through game widget
    game = ObjectProperty(None)

    # All characters have the following properties
    start_x = NumericProperty(0)
    start_y = NumericProperty(0)
    start_position = ReferenceListProperty(start_x, start_y)

    x_position = NumericProperty(0)
    y_position = NumericProperty(0)
    grid_position = ReferenceListProperty(x_position, y_position)

    speed = NumericProperty(0)
    speed_multiplier = NumericProperty(1)
    color = ObjectProperty((0, 0, 0))

    current_direction = ObjectProperty(direction.Direction.right)
    next_direction = ObjectProperty(direction.Direction.right)

    angle = NumericProperty()

    def move(self):
        """Move the character.

        This method moves the character and ensures
        that characters are positioned correctly. It should be
        called every frame.
        """

        # Copy of previous window position
        previous_position = self.center[:]
        new_position = Vector(self.current_direction.value[0] * self.speed,
                          self.current_direction.value[1] * self.speed) + self.pos
        self.pos = new_position

        self._check_position()
        self._update_direction((previous_position))
        self._update_position()

    def initialise(self):
        """Initialise the character's size, position and direction.

        This method sets the character widget to the correct inital position,
        ensures that it is the size of the cell interiors, and initialises the
        current and next directions.
        """

        self.initialise_direction()
        starting_cell = self.game.level.get_cell(self.start_position)
        # Size must be set first or it does it incorrectly
        self.initialise_size(starting_cell)
        self.initialise_position(starting_cell)

    def initialise_direction(self):
        """Initialise the starting directions of the characters.

        This method initialises the starting directions of the characters.
        All characters start facing right.
        This method should be called when a new game/level is started, or
        when the player dies.
        """

        self.current_direction = direction.Direction.right
        self.next_direction = direction.Direction.right
        self.angle = self.current_direction.get_angle()

    def initialise_position(self, starting_cell):
        self.grid_position = starting_cell.coordinates
        self.center = starting_cell.center

    def initialise_size(self, starting_cell):
        # Set size to interior of cell size
        self.size = starting_cell.interior

    def update_character(self):
        """Update the character's size and position relative to the level.

        This method ensures that the character's size and position is
        correct relative to the level, and that the character is in the
        center of its stored cell. This method should be called whenever the
        window size changes.
        """
        # So that size and position is correct if window size changes
        current_cell = self.game.level.get_cell(self.grid_position)
        self.center = current_cell.center
        self.size = current_cell.interior

    def _check_position(self):
        """Ensure the character cannot move through walls.

        This method moves the character back to the center of its current cell
        if it attempts to move into a wall. This method should be called every
        frame, after the character has been moved.
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
        """Check pending movement direction and change direction if possible.

        If there is a pending movement direction, this method checks if movement
        in that direction is possible. If it is possible, the current direction is
        set to the pending direction, and the character is moved to the center of the
        current cell to ensure correct positioning.

        Arguments:
        (previous_x, previous_y) -- a tuple of the character's window coordinates on the previous frame
        """
        if self.next_direction != self.current_direction:
            current_cell = self.game.level.cells[self.x_position][self.y_position]
            current_edge = current_cell.get_edge(self.next_direction)

            if current_edge.type == level_cell.CellEdgeType.passage:
                if self.current_direction == direction.Direction.right:
                    # Set new direction for next frame if character has moved into/past center or is at the center of cell
                    if ((self.center_x >= current_cell.center_x and current_cell.center_x > previous_x) or
                            (self.center_x == current_cell.center_x and previous_x == current_cell.center_x)):
                        # Ensure player is in center before changing direction
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
        """Set the current direction to the pending direction"""
        self.current_direction = self.next_direction
        self.angle = self.current_direction.get_angle()

    def _update_position(self):
        """Update the stored position of the player in grid coordinates"""
        grid_position = self.game.level.convert_to_grid_position(self.center)
        self.grid_position = grid_position


class PlayerBeetle(Character):

    """Store methods and properties relevant to the player character.

    This class stores methods and properties relating to only the player,
    namely checking if the player has collided with an enemy or is dead.

    Kivy Events:
    on_last_chomp_high -- alternate the chomp sound
    on_grid_position -- check for enemy collisions
    on_dead -- remove life if player is dead

    Kivy Properties:
    color -- ObjectProperty storing the color of the character
    dead -- BooleanProperty storing whether the player is dead or not
    """

    color = ObjectProperty((1, 1, 0))
    dead = BooleanProperty(False)
    powered_up = BooleanProperty(False)

    last_chomp_high = BooleanProperty()
    chomp_sound = ObjectProperty()

    def initialise(self):
        self.__initialise_chomp_sound()
        self.__initialise_modes()
        Character.initialise(self)

    def __check_pellet_collision(self):
        """Check for pellet collision.

        This method checks if the player has collided with any pellets.
        If so, the score is adjusted or a power-up is applied appropriately.
        """

        current_cell = self.game.level.get_cell(self.grid_position)
        if current_cell.pellet_exists:
            if current_cell.pellet.type == collectable.PelletType.power:
                self.powered_up = True
                self.__frighten_enemies()
            self.__eat_pellet(current_cell)

    def __check_enemy_collision(self):
        """Check for enemy collisions.

        This method checks if the player is in the same grid position as an
        enemy. If so, the player is set to dead. If the player has a power-up, the
        player is not set to dead and the enemy retreats to the beetle den.
        """

        if self.game.game_active:
            for enemy in self.game.enemies:
                if enemy.grid_position == self.grid_position:
                    if self.powered_up and enemy.fleeing:
                        enemy.dead = True
                    elif not enemy.dead:
                        self.dead = True

    def __remove_life(self):
        self.powered_up = False
        self.game.lives -= 1
        self.dead = False

    def __eat_pellet(self, current_cell):
        current_cell.remove_pellet()
        self.game.score += self.game.pellet_value
        self.chomp_sound.play()
        self.last_chomp_high = not self.last_chomp_high
        self.game.pellet_count -= 1

    def __activate_powerup(self):
        Clock.unschedule(self.__remove_powerup)
        self.game.sounds['power_up'].play()
        # Color change temporary for testing
        self.color = (0, 1, 0)
        Clock.schedule_once(self.__remove_powerup, self.game.powerup_length)

    def __frighten_enemies(self):
        for enemy in self.game.enemies:
            enemy.pause_mode_change()
            if self.game.level.get_cell(enemy.grid_position) not in self.game.level.beetle_house.itervalues():
                enemy.fleeing = True

    def __remove_powerup(self, dt):
        """Remove the power-up status from the player."""
        self.powered_up = False

    def __initialise_chomp_sound(self):
        # Always start with high note
        self.last_chomp_high = False

    def __initialise_modes(self):
        self.powered_up = False
        self.dead = False

    def on_powered_up(self, instance, value):
        if self.powered_up:
            self.__activate_powerup()
            if self.game.sounds['frightened'].state == 'stop':
                self.game.sounds['frightened'].loop = True
                self.game.sounds['frightened'].play()
        else:
            self.game.sounds['frightened'].stop()
            self.color = (1, 1, 0)
            for enemy in self.game.enemies:
                enemy.fleeing = False
                enemy.resume_mode_change()

    def on_last_chomp_high(self, instance, value):
        if self.last_chomp_high:
            self.chomp_sound = self.game.sounds["chomp_low"]
        else:
            self.chomp_sound = self.game.sounds["chomp_high"]

    def on_grid_position(self, instance, value):
        """Check for enemy and pellet collisions on grid position change.

        When the player grid position changes, this kivy event is called
        and checks if player has collided with an enemy or pellet.
        """
        self.__check_pellet_collision()
        self.__check_enemy_collision()

    def on_dead(self, instance, value):
        """Check if the player is dead and remove a life if so.

        This is kivy event called when player's dead status changes. If
        the player is dead, a life is removed and the player is set to
        not dead.
        """

        if self.dead:
             self.__remove_life()
        else:
            # Do nothing if set to alive
            pass


class EnemyBeetle(Character):

    """Store methods and properties relating only to enemy characters.

    This class stores methods and properties relevant to enemy characters.
    The general enemy movement behaviour and decision making is defined in this class.

    Kivy Properties:
    pursuing -- BooleanProperty that indicates which mode the enemy is in
    dormant -- BooleanProperty that indicates whether the enemy is dormant
    mode_change_timer -- the number of seconds the next mode change will be scheduled for

    Public Methods:
    reset_scatter_timers -- reset the mode to scatter and the timer to its initial state
    reset_release_timers -- reset the mode to dormant and the timer to its initial state
    """

    pursuing = BooleanProperty(False)
    dormant = BooleanProperty(True)
    fleeing = BooleanProperty(False)

    dead = BooleanProperty(False)

    scatter_length = NumericProperty()
    chase_length = NumericProperty()
    mode_change_timer = NumericProperty()

    mode_change_start = NumericProperty()
    mode_time_remaining = NumericProperty()

    def initialise(self):
        self._initialise_chase_mode()
        self._initialise_flee_mode()
        Character.initialise(self)

    def reset_character(self):
        self.__unschedule_all_timers()
        self.__deactivate()
        self._initialise_mode_lengths()
        self._set_start_position()
        self.initialise()

    def start_scatter_timer(self):
        """Reset the mode to scatter and the timer to its initial state.

        This method resets the pursuing/scatter state and resets the timer.
        It should be called when the player dies or a new game/level is started.
        """

        Clock.unschedule(self.__change_mode)
        self.mode_change_timer = self.scatter_length
        Clock.schedule_once(self.__change_mode, self.mode_change_timer)

    def start_release_timer(self):
        """Reset the enemy state to dormant and the activation timer to its inital state.

        This method resets the enemy state to dormant and resets its release timer.
        It should only be called when a new game or level is started.
        """

        Clock.unschedule(self.__activate)
        Clock.schedule_once(self.__activate, self.activation_timer)

    def __unschedule_all_timers(self):
        Clock.unschedule(self.__activate)
        Clock.unschedule(self.__change_mode)

    def move(self):
        self._set_next_direction()
        Character.move(self)

    def retreat(self):
        """Move the enemy to the beetle den.

        This method moves the enemy to the beetle den if it is dead.
        The enemy is set to not dead upon reaching the beetle den.
        This method should be called every frame in place of move if
        the enemy is dead.
        """

        beetle_house_center = self.game.level.beetle_house['center'].center
        direction_vector =  Vector(beetle_house_center) - Vector(self.center)
        direction_vector = direction_vector.normalize()

        if not self.collide_point(*beetle_house_center):
            self.pos = (direction_vector * self.game.speed_multiplier) + Vector(self.pos)
        else:
            self.center = beetle_house_center
            self.dead = False
            self.fleeing = False

    def _set_next_direction(self):
        """Set the next intended movement direction."""
        if self.dormant:
            current_cell = self.game.level.get_cell(self.grid_position)
            if current_cell.get_edge(self.current_direction).type == level_cell.CellEdgeType.wall:
                self.next_direction = self.current_direction.get_opposite()

        elif self.fleeing:
            possible_moves = self.__get_possible_moves()
            self.next_direction = self.__get_random_move(possible_moves)

        else:
            if self.game.level.get_cell(self.grid_position) == self.game.level.beetle_house['center']:
                self.target_position = self.game.level.beetle_house['center'].coordinates + Vector(0, 1)
                self.next_direction = direction.Direction.up
            else:
                self.target_position = self._get_target_position()
                possible_moves = self.__get_possible_moves()
                best_move = self.__get_shortest_move(possible_moves)
                self.next_direction = best_move

    def _initialise_chase_mode(self):
        self.pursuing = False

    def _initialise_flee_mode(self):
        self.fleeing = False

    def _initialise_mode_lengths(self):
        self.scatter_length = self.game.scatter_length
        self.chase_length = self.game.chase_length

    def __change_mode(self, dt):
        """Switch enemy between scatter and chase mode.

        This method switches the enemy state between pursuing and not
        pursuing, as well as reversing enemy direction to signify the change.
        After the mode is changed, the timer for this method being called again
        is set depending on the mode that the enemy is now in.
        """
        self.pursuing = not self.pursuing
        self.current_direction = self.current_direction.get_opposite()
        self.mode_change_start = Clock.get_time()

        if self.pursuing:
            self.mode_change_timer = self.chase_length
            Clock.schedule_once(self.__change_mode, self.mode_change_timer)
        else:
            self.mode_change_timer = self.scatter_length
            Clock.schedule_once(self.__change_mode, self.mode_change_timer)

    def __deactivate(self):
        self.dormant = True

    # Needed to be a method to schedule on Clock
    def __activate(self, dt):
        """Change enemy state from dormant to active"""
        self.dormant = False

    def __get_possible_moves(self):
        """Return a list of directions the enemy is allowed to move in."""

        # List in this order means priority is up-left-down-right when using directions.pop
        directions = [direction.Direction.right,
                      direction.Direction.down,
                      direction.Direction.left,
                      direction.Direction.up]
        possible_directions = [dir for dir in directions if self.__direction_is_allowed(dir)]
        return possible_directions

    def __get_shortest_move(self, possible_moves):
        """Return the best direction the enemy can move in.

        This method returns the direction that results in the enemy being in
        the cell nearest the target cell as a direction.Direction.

        Arguments:
        possible_moves -- a list of directions the enemy is allowed to travel in
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

    def __get_random_move(self, possible_moves):
        """Return a random direction.

        This method returns a random direction from a given
        list of possible moves.

        Arguments:
        possible_moves -- a list of directions the enemy is allowed to travel in
        """

        return random.choice(possible_moves)

    def __direction_is_allowed(self, direction):
        """Return true if the enemy is allowed to travel in the given direction.

        This function determines whether the enemy is allowed to travel in a
        given. The enemy is not allowed to travel through walls or in the opposite
        direction to its current direction of travel (unless it is in the beetle house).

        Arguments:
        direction -- direction to be checked (as a direction.Direction)
        """

        current_cell = self.game.level.get_cell(self.grid_position)
        # Cannot move in the direction if there is a wall
        if current_cell.get_edge(direction).type == level_cell.CellEdgeType.wall:
            return False
        elif direction == self.current_direction.get_opposite():
            # If enemy is in the beetle house, opposite direction is allowed
            if self.game.level.get_cell(self.grid_position) in self.game.level.beetle_house.itervalues():
                return True
            else:
                return False
        else:
            return True

    def pause_mode_change(self):
        """Pause the mode change timers.

        This method pauses the mode change timers. It should be
        called when the enemies become frightened.
        """

        Clock.unschedule(self.__change_mode)
        pause_time = Clock.get_time()
        time_into_mode = pause_time - self.mode_change_start

        if self.pursuing:
            self.mode_time_remaining = self.chase_length - time_into_mode
        elif not self.pursuing:
            self.mode_time_remaining = self.scatter_length - time_into_mode

    def resume_mode_change(self):
        """Resume the mode change timers.

        This method resumes the mode change timers. It should
        be called when the enemies stop being frightened.
        """

        Clock.schedule_once(self.__change_mode, self.mode_time_remaining)

    def on_grid_position(self, instance, value):
        """Check for collision with player on grid position change.

        When the enemy's grid position changes, this Kivy event is called
        and checks if it has collided with the player. The player state is
        set to dead if it has.
        This needs to be checked when the enemy moves as well as when the
        player moves, in case one is stationary.
        """

        if self.game.player.grid_position == self.grid_position:
            if self.game.player.powered_up and self.fleeing:
                self.dead = True
            elif not self.dead:
                self.game.player.dead = True

    def on_fleeing(self, instance, value):
        """Check if the enemy is fleeing and change its colour.
        """

        if self.fleeing:
            self.color = (255, 255, 255)

        else:
            self.color = (255, 0, 0)


    def on_dead(self, instance, value):
        """Check if the enemy is dead."""
        if self.dead:
            self.game.sounds['retreat'].play()

class RedBeetle(EnemyBeetle):

    """Store methods and properties specific to the Red Beetle.

    Kivy Properties:
    color -- ObjectProperty storing the color of the character
    activation_timer -- NumericProperty representing the number of seconds until enemy is released
    """

    color = ObjectProperty((1, 0, 0))
    activation_timer = NumericProperty(0)

    def _set_start_position(self):
        """Set the start position of the enemy.

        This method sets the start position of the enemy.
        The red beetle starts in the center of the beetle house.
        The start position for enemies cannot be set in the kv
        file as it is dynamic."""
        self.start_position = self.game.level.beetle_house['center'].coordinates

    def _get_target_position(self):
        """Determine and return the target position.

        This method returns the target position depending on the enemy's mode.
        The red beetle's target position is the player's position when pursuing.
        The target position is the upper right corner when scattering.
        """
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

    """Store methods and properties specific to the Pink Beetle.

    Kivy Properties:
    color -- ObjectProperty storing the color of the character
    activation_timer -- NumericProperty representing the number of seconds until enemy is released
    """

    color = ObjectProperty((1, 0, 1))
    activation_timer = NumericProperty(10)

    def _set_start_position(self):
        """Set the start position of the enemy.

        This method sets the start position of the enemy.
        The pink beetle starts in the center of the beetle house.
        The start position for enemies cannot be set in the kv
        file as it is dynamic.
        """

        self.start_position = self.game.level.beetle_house['center'].coordinates

    def _get_target_position(self):
        """Determine and return the target position

        This method returns the target position depending on the enemy's mode.
        The pink beetle's target position is two spaces ahead of the player's position
        when pursuing.
        The target position is the upper left corner when scattering.
        """

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

    """Store methods and properties specific to the Blue Beetle.

    Kivy Properties:
    color -- ObjectProperty storing the color of the character
    activation_timer -- NumericProperty representing the number of seconds until enemy is released
    """

    color = ObjectProperty((0, 1, 1))
    activation_timer = NumericProperty(20)

    def _set_start_position(self):
        """Set the start position of the enemy.

        This method sets the start position of the enemy.
        The blue beetle starts at the right of the beetle house.
        The start position for enemies cannot be set in the kv
        file as it is dynamic.
        """

        self.start_position = self.game.level.beetle_house['right'].coordinates

    def _get_target_position(self):
        """Determine and return the target position

        This method returns the target position depending on the enemy's mode.
        The blue beetle's target position is the twice the vector between the
        player's position and the red beetles position when pursuing.
        The target position is the lower right corner when scattering.
        """

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

    """Store methods and properties specific to the Orange Beetle.

    Kivy Properties:
    color -- ObjectProperty storing the color of the character
    activation_timer -- NumericProperty representing the number of seconds until enemy is released
    flee_distance -- NumericProperty representing the distance from the player the enemy needs to be less than to flee
    """

    color = ObjectProperty((1, 0.5, 0))
    activation_timer = NumericProperty(30)
    flee_distance = NumericProperty(4)

    def _set_start_position(self):
        """Set the start position of the enemy.

        This method sets the start position of the enemy.
        The orange beetle starts at the left of the beetle house.
        The start position for enemies cannot be set in the kv
        file as it is dynamic.
        """

        self.start_position = self.game.level.beetle_house['left'].coordinates

    def _get_target_position(self):
        """Determine and return the target position

        This method returns the target position depending on the enemy's mode.
        The orange beetle's target position is the player's position when the distance
        away from the player is greater than flee_distance. It is the same as its
        scatter target if the distance is less than flee_distance.
        The target position is the lower left corner when scattering.
        """
        if self.pursuing:
            player_position = self.game.player.grid_position
            distance_from_player = Vector(player_position).distance(self.grid_position)

            if distance_from_player > self.flee_distance:
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








