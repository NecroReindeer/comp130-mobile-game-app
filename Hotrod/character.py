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

# Standard python libraries
import random

# Kivy modules
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.properties import NumericProperty
from kivy.properties import ReferenceListProperty
from kivy.properties import BooleanProperty
from kivy.properties import StringProperty
from kivy.vector import Vector
from kivy.clock import Clock

# Own modules
import collectable
import direction
import level_cell


# Time that the character will start flashing before powerup ends in seconds
POWERUP_END_WARNING_TIME = 0.5


class Character(Widget):

    """Store methods and properties relevant to all characters.

    All characters inherit from this class. It includes methods that
    are universal to all characters, such as those managing movement.

    Public methods:
    move() -- move the character. Should be called every frame.
    initialise() -- set up the size and position of the character
    update_character() -- ensure that the size and position is correct
    kill_character() -- set the character to dead
    """

    # All characters have the following properties
    start_x = NumericProperty(0)
    start_y = NumericProperty(0)
    start_position = ReferenceListProperty(start_x, start_y)

    x_position = NumericProperty(0)
    y_position = NumericProperty(0)
    grid_position = ReferenceListProperty(x_position, y_position)

    speed = NumericProperty(0)

    current_direction = ObjectProperty(direction.Direction.right)
    next_direction = ObjectProperty(direction.Direction.right)

    # Determines the angle the character is displayed
    rotation_angle = NumericProperty()
    source_image = StringProperty()

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

        self._check_position_validity()
        self._update_direction(previous_position)
        self._update_grid_position()

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

    def initialise(self):
        """Initialise the character's size, position and direction.

        This method sets the character widget to the correct inital position,
        ensures that it is the size of the cell interiors, and initialises the
        current and next directions.
        """

        starting_cell = self.game.level.get_cell(self.start_position)

        # I made these all separate functions to reduce confusion
        self.__initialise_direction()
        # Size must be set before position or it does it incorrectly
        self.__initialise_size(starting_cell)
        self.__initialise_position(starting_cell)
        self.__initialise_image()
        self._initialise_bindings()

    def kill_character(self):
        """Set the character to dead."""

        self.dead = True

    def __initialise_direction(self):
        """Initialise the starting directions of the characters.

        This method initialises the starting directions of the characters.
        All characters start facing right.
        This method should be called when a new game/level is started, or
        when the player dies.
        """

        self.current_direction = direction.Direction.right
        self.next_direction = direction.Direction.right
        self.rotation_angle = self.current_direction.get_angle()

    def __initialise_position(self, starting_cell):
        self.grid_position = starting_cell.coordinates
        self.center = starting_cell.center

    def __initialise_size(self, starting_cell):
        """Set the character's size to the interior of the cell."""

        # Set size to interior of cell size
        self.size = starting_cell.interior

    def __initialise_image(self):
        """Set the character's source image to their normal image."""

        self.source_image = self.normal_image

    def _initialise_bindings(self):
        """Create any Kivy bindings for the characters."""

        self.bind(grid_position=self.game.play_area.check_character_collisions)

    def _check_position_validity(self):
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
        """Set the current direction to the pending next direction."""

        self.current_direction = self.next_direction

    def _update_grid_position(self):
        """Update the stored position of the character.

        This method updates the stored position of the character in grid
        coordinates relative to the level's cells.
        """

        grid_position = self.game.level.convert_to_grid_position(self.center)
        self.grid_position = grid_position

    def on_current_direction(self, instance, value):
        """Ensure that the character rotation is correct.

        This Kivy event is called when the current direction changes.
        It ensures that the character's angle is changed whenever
        the direction changes.
        """

        if self.game.game_active:
            self.rotation_angle = self.current_direction.get_angle()


class PlayerBeetle(Character):

    """Store methods and properties relevant to the player character.

    This class stores methods and properties relating to only the player,
    namely checking if the player has collided with an enemy or is dead.

    Kivy Events:
    on_last_chomp_high -- alternate the chomp sound
    on_dead -- remove life if player is dead

    Kivy Properties:
    dead -- BooleanProperty storing whether the player is dead or not
    powered_up -- BooleanProperty storing whether the player is powered up
    last_chomp_high -- BooleanProperty storing whether the last chomp sound was high
    chomp_sound -- ObjectProperty for storing the sound to be used as chomp
    """

    dead = BooleanProperty(False)
    powered_up = BooleanProperty(False)
    last_chomp_high = BooleanProperty()
    chomp_sound = ObjectProperty()

    def initialise(self):
        """Initialise the player character.

        This method performs initialisations specific for the player
        character, such as chomp sound and power-up mode. It also
        performs the initialisations relevant to all characters.
        """

        self.__initialise_chomp_sound()
        self.__initialise_states()
        Character.initialise(self)

    def activate_powerup(self, instance, value):
        """Ensure that powerup is activated correctly.

        This method fully activates the powerup, by scheduling
        the method that removes the powerup for the appropriate amount of time.
        It also schedules the method that makes the player character flash
        when the powerup is about to run out.
        """

        # Unschedule remove powerup so that full length of additional pellets is experienced
        Clock.unschedule(self.__remove_powerup)
        Clock.unschedule(self.__indicate_powerup_end)
        self.game.sounds['power_up'].play()
        self.powered_up = True
        Clock.schedule_once(self.__remove_powerup, self.game.powerup_length)
        Clock.schedule_once(self.__indicate_powerup_end, self.game.powerup_length - POWERUP_END_WARNING_TIME)

    def __initialise_chomp_sound(self):
        """Initialise the chomp sound.

        This method initialises the sound played when the player
        eats a pellet so that it begins with the high note.
        """

        # Always start with high note
        self.last_chomp_high = False

    def __initialise_states(self):
        """Initialise power-up and dead states.

        This method initialises the power-up and dead states
        of the player, so that it starts not dead and not
        powered up.
        """

        # Start not dead and not powered up
        self.powered_up = False
        self.dead = False

    def _initialise_bindings(self):
        for enemy in self.game.enemies:
            self.bind(powered_up=enemy.switch_frightened_state)
        Character._initialise_bindings(self)

    def __check_pellet_collision(self):
        """Check for pellet collisions.

        This method checks if the player has collided with any pellets.
        If so, the score is adjusted or a power-up is applied appropriately.
        """

        current_cell = self.game.level.get_cell(self.grid_position)
        if current_cell.pellet_exists:
            self.__eat_pellet(current_cell)

    def __eat_pellet(self, current_cell):
        """Remove the pellet.

        This method removes the pellet of the given cell, plays the
        chomp sound, increases the score and decreases the pellet
        counter. It also switches the last_chomp_high bool.
        """

        current_cell.remove_pellet()
        self.game.score += self.game.pellet_value
        self.chomp_sound.play()
        self.last_chomp_high = not self.last_chomp_high

    def __remove_powerup(self, dt):
        """Remove the power-up status from the player.

        This method is scheduled on the Kivy clock and sets the
        player's powered up state to false when called.
        """

        # This is in a method so that it can be scheduled
        self.powered_up = False

    def __indicate_powerup_end(self, dt):
        """Indicate that the powerup is about to end.

        This method is scheduled on the Kivy clock and makes the
        player character flash between its powered up and normal
        image until the power up ends.
        """

        if self.powered_up:
            if self.source_image == self.normal_image:
                self.source_image = self.power_image

            elif self.source_image == self.power_image:
                self.source_image = self.normal_image
            Clock.schedule_once(self.__indicate_powerup_end, 0.1)

    def on_powered_up(self, instance, value):
        """Activate and deactivate the powerup.

        This Kivy event is triggered when the players power up
        state changes. If the player is powered up, the frightened
        noise is played and the player's image is changed.

        Note: The things in this method are things that
        should happen only when the player changes state between
        powered-up and not powered-up, not the things that should
        happen when the player collects a power-up.
        """

        if self.powered_up:
            # Only these are to be done on initial collection
            self.source_image = self.power_image
            if self.game.sounds['frightened'].state == 'stop':
                self.game.sounds['frightened'].play()
        else:
            # Here so that these are still reset on death whilst powered up
            self.game.sounds['frightened'].stop()
            self.source_image = self.normal_image

    def on_last_chomp_high(self, instance, value):
        """Alternate the chomp sound.

        This Kivy event is triggered when the bool storing what
        the last chomp was is changed. It alternates which sound
        file is used for chomp
        """

        if self.last_chomp_high:
            self.chomp_sound = self.game.sounds["chomp_low"]
        else:
            self.chomp_sound = self.game.sounds["chomp_high"]

    def on_grid_position(self, instance, value):
        """Check for pellet collisions on grid position change.

        When the player grid position changes, this Kivy event is called
        and checks if player has collided with a pellet.
        """

        self.__check_pellet_collision()

    def on_dead(self, instance, value):
        """Check if the player is dead and remove a life if so.

        This is Kivy event called when player's dead status changes. If
        the player is dead, powerup and a life is removed and the player
        is set back to not dead.
        """

        if self.dead:
            self.game.lives -= 1
            self.powered_up = False


class EnemyBeetle(Character):

    """Store methods and properties relating only to enemy characters.

    This class stores methods and properties relevant to enemy characters.
    The general enemy movement behaviour and decision making is defined in this class.

    Kivy Properties:
    pursuing -- BooleanProperty that indicates which mode the enemy is in
    dormant -- BooleanProperty that indicates whether the enemy is dormant
    frightened -- BooleanProperty that indicates whether the enemy is frightened
    dead -- BooleanProperty that indicates whether the enemy is dead
    scatter_length -- NumericProperty representing the length of scatter mode
    chase_length -- NumericProperty representing the length of chase mode
    mode_change_timer -- the number of seconds the next mode change will be scheduled for
    mode_change_start -- stores when the last mode change was for pausing it
    mode_time_remaining -- stores how much time remaining until mode change for resuming it

    Public Methods:
    move -- move the enemy.
    reset_scatter_timers -- reset the mode to scatter and the timer to its initial state
    reset_release_timers -- reset the mode to dormant and the timer to its initial state
    """

    dormant = BooleanProperty(True)
    pursuing = BooleanProperty(False)
    frightened = BooleanProperty(False)
    dead = BooleanProperty(False)

    scatter_length = NumericProperty()
    chase_length = NumericProperty()
    mode_change_timer = NumericProperty()

    mode_change_start = NumericProperty()
    mode_time_remaining = NumericProperty()
    mode_change_paused = BooleanProperty(False)

    def move(self):
        """Move the character.

        This method carries out things specific to enemy movement,
        as well as calling back to the general character movement.
        If the enemy is dead, movement is handled differently.
        """

        if self.dead:
            self.retreat()
        else:
            self._set_next_direction()
            Character.move(self)

    def retreat(self):
        """Move the enemy to the beetle den.

        This method moves the enemy to the beetle den if it is dead.
        The enemy is set to not dead upon reaching the beetle den.
        This method should be called every frame in place of move if
        the enemy is dead.
        """

        beetle_den_center = self.game.level.beetle_den['center']
        beetle_den_center_coords = beetle_den_center.center
        direction_vector = Vector(beetle_den_center_coords) - Vector(self.center)
        direction_vector = direction_vector.normalize()

        if not self.collide_point(*beetle_den_center_coords):
            self.pos = (direction_vector * self.speed) + Vector(self.pos)
        else:
            self.center = beetle_den_center_coords
            # Reset here as rare bug sometimes happens where grid coordinates not set before move
            self.grid_position = beetle_den_center.coordinates
            self.dead = False
            self.frightened = False

    def initialise(self):
        """Initialise the enemy characters.

        This method performs initialisations specific for the enemies,
        such as setting their initial modes.
        performs initialisations relevant to all characters.
        It should be called when the player dies or a new game/level is
        started.
        """

        self.__initialise_bindings()
        self.__initialise_chase_mode()
        self.__initialise_flee_mode()
        Character.initialise(self)

    def reset_character(self):
        """Reset the enemy characters.

        This method performs the basic initialisations, in addition to
        things that should only be reset upon starting a new game or
        level.
        """

        self.__unschedule_all_timers()
        self.__deactivate()
        self.__reset_mode_lengths()
        self._set_start_position()
        self.initialise()

    def start_scatter_timer(self):
        """Reset the scatter/chase timer to its initial state.

        This method resets the pursuing/scatter state timer.
        It should be called when the player dies or a new game/level is started.
        """

        Clock.unschedule(self.__change_mode)
        self.mode_change_timer = self.scatter_length
        Clock.schedule_once(self.__change_mode, self.mode_change_timer)

    def start_release_timer(self):
        """Reset the activation timer to its initial state.

        This method resets the enemy's release timer.
        It should only be called when a new game or level is started.
        """

        Clock.unschedule(self.__activate)
        Clock.schedule_once(self.__activate, self.activation_timer)

    def __initialise_chase_mode(self):
        """Set chase state to initial value."""

        self.pursuing = False

    def __initialise_flee_mode(self):
        """Set flee mode to initial value."""

        self.frightened = False

    def __initialise_bindings(self):
       pass

    def __reset_mode_lengths(self):
        """Reset the length of the scatter and chase mode."""

        self.scatter_length = self.game.scatter_length
        self.chase_length = self.game.chase_length

    def __unschedule_all_timers(self):
        """Unschedule all enemy timers."""

        Clock.unschedule(self.__activate)
        Clock.unschedule(self.__change_mode)

    def _set_next_direction(self):
        """Set the next intended movement direction.

        This method sets the enemies next intended movement direction.
        It should be called every frame.
        The chosen movement direction depends on what mode the enemy is
        in, as well as the enemy's target position.
        """

        if self.dormant:
            current_cell = self.game.level.get_cell(self.grid_position)
            if current_cell.get_edge(self.current_direction).type == level_cell.CellEdgeType.wall:
                self.next_direction = self.current_direction.get_opposite()

        elif self.frightened:
            possible_moves = self.__get_possible_moves()
            self.next_direction = self.__get_random_move(possible_moves)

        else:
            if self.game.level.get_cell(self.grid_position) == self.game.level.beetle_den['center']:
                self.target_position = self.game.level.beetle_den['center'].coordinates + Vector(0, 1)
                self.next_direction = direction.Direction.up
            else:
                self.target_position = self._get_target_position()
                possible_moves = self.__get_possible_moves()
                best_move = self.__get_shortest_move(possible_moves)
                self.next_direction = best_move

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

        print self, "New mode: ", self.pursuing, Clock.get_time()

    def __deactivate(self):
        """Change enemy state to active."""
        self.dormant = True

    # Needed to be a method to schedule on Clock
    def __activate(self, dt):
        """Change enemy state to dormant"""
        self.dormant = False

    def __get_possible_moves(self):
        """Return a list of directions the enemy is allowed to move in.

        This method returns a list of directions the enemy is allowed to
        move in. The directions are prioritied up-left-down-right.
        """

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
                # This ensures that distances are added in both distance order and priority order
                shortest_distance = distance
                best_moves.append(move)
        # Returns the shortest move that is the highest priority in up-left-down-right
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
        direction -- direction to be checked as a direction.Direction
        """

        current_cell = self.game.level.get_cell(self.grid_position)
        # Cannot move in the direction if there is a wall
        if current_cell.get_edge(direction).type == level_cell.CellEdgeType.wall:
            return False
        elif direction == self.current_direction.get_opposite():
            # If enemy is in the beetle house, opposite direction is allowed
            if self.game.level.get_cell(self.grid_position) in self.game.level.beetle_den.itervalues():
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

        print "Pausing at ", str(pause_time)
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

        print "Resuming at ", str(Clock.get_time())

        Clock.schedule_once(self.__change_mode, self.mode_time_remaining)

    def switch_frightened_state(self, instance, value):
        """Switch the frightened state.

        This Kivy event should be called when the players powered-up state
        has changed or a cell containing a power pellet's pellet existence
        state changes.
        This method switches the enemies' frightened states to correspond
        with the players powered up state and pauses/resumes regular scatter/chase
        mode changes accordingly.
        """

        if self.game.player.powered_up:
            if self.game.level.get_cell(self.grid_position) not in self.game.level.beetle_den.itervalues():
                self.frightened = True
            # Paused here rather than in on_fleeing as all enemies need pausing
            self.pause_mode_change()
        else:
            self.frightened = False
            # Resumed here rather than in on_fleeing as should only happen when powerup wears off
            self.resume_mode_change()

    def on_frightened(self, instance, value):
        """Check if the enemy is fleeing and change its image accordingly.

        This Kivy event is called when the enemy's fleeing state changes.
        It changes the colour accordingly.
        """

        if self.frightened:
            self.source_image = self.frightened_image
        else:
            self.source_image = self.normal_image

    def on_dead(self, instance, value):
        """Check if the enemy is dead and play a sound if so.

        This Kivy event is called when the enemy's dead state is
        changed. If the enemy has changed to dead, a sound is played.
        """

        if self.dead:
            self.game.score += self.game.kill_value
            self.game.sounds['retreat'].play()


class RedBeetle(EnemyBeetle):

    """Store methods and properties specific to the Red Beetle.

    Kivy Properties:
    activation_timer -- NumericProperty representing the number of seconds until enemy is released
    """

    def _set_start_position(self):
        """Set the start position of the enemy.

        This method sets the start position of the enemy.
        The red beetle starts in the center of the beetle den.
        The start position for enemies cannot be set in the kv
        file as it is dynamic."""
        self.start_position = self.game.level.beetle_den['center'].coordinates

    def _get_target_position(self):
        """Determine and return the target position.

        This method returns the target position depending on the enemy's mode.
        The red beetle's target position is the player's position when pursuing.
        The target position is the upper right corner when scattering.
        """

        if self.pursuing:
            # Target position is always player's position
            return self.game.player.grid_position
        else:
            # Upper right corner
            target_position = (self.game.level.columns + 1, self.game.level.rows + 1)
            return target_position


class PinkBeetle(EnemyBeetle):

    """Store methods and properties specific to the Pink Beetle.

    Kivy Properties:
    activation_timer -- NumericProperty representing the number of seconds until enemy is released
    """

    def _set_start_position(self):
        """Set the start position of the enemy.

        This method sets the start position of the enemy.
        The pink beetle starts in the center of the beetle den.
        The start position for enemies cannot be set in the kv
        file as it is dynamic.
        """

        self.start_position = self.game.level.beetle_den['center'].coordinates

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
            # Target position is 2 cells ahead of the player
            target_position = Vector(player_position) + (2 * player_direction_vector)
            return target_position

        else:
            # Upper left corner in scatter mode
            target_position = (-1, self.game.level.rows + 1)
            return target_position


class BlueBeetle(EnemyBeetle):

    """Store methods and properties specific to the Blue Beetle.

    Kivy Properties:
    activation_timer -- NumericProperty representing the number of seconds until enemy is released
    """

    def _set_start_position(self):
        """Set the start position of the enemy.

        This method sets the start position of the enemy.
        The blue beetle starts at the right of the beetle den.
        The start position for enemies cannot be set in the kv
        file as it is dynamic.
        """

        self.start_position = self.game.level.beetle_den['right'].coordinates

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
            two_cells_ahead_of_player = Vector(player_position) + (2 * player_direction_vector)
            red_beetle_position = self.game.red_enemy.grid_position
            # Target position is double the vector between 2 spaces ahead of the player and the red beetle
            target_position = 2 * Vector(two_cells_ahead_of_player) - Vector(red_beetle_position)
            return target_position

        else:
            # Bottom right in scatter mode
            target_position = (self.game.level.columns + 1, -1)
            return target_position


class OrangeBeetle(EnemyBeetle):

    """Store methods and properties specific to the Orange Beetle.

    Kivy Properties:
    activation_timer -- NumericProperty representing the number of seconds until enemy is released
    flee_distance -- NumericProperty representing the distance from the player the enemy needs to be less than to flee
    """

    def _set_start_position(self):
        """Set the start position of the enemy.

        This method sets the start position of the enemy.
        The orange beetle starts at the left of the beetle den.
        The start position for enemies cannot be set in the kv
        file as it is dynamic.
        """

        self.start_position = self.game.level.beetle_den['left'].coordinates

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
            return target_position

        else:
            # Bottom left in scatter mode
            target_position = -1, -1
            return target_position








