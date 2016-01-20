import json
import random
import os
import sys

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.properties import NumericProperty
from kivy.properties import BooleanProperty
from kivy.properties import ListProperty
from kivy.properties import StringProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.config import Config
from kivy.uix.button import Button
from kivy.core.audio import SoundLoader
from kivy.core.audio.audio_sdl2 import SoundSDL2
from kivy.network.urlrequest import UrlRequest

import direction
import level
import level_cell
import character
import user_interface

# Game to run at 60 frames per second
FPS = 60
# The relative location of the game's sound files
SOUND_DIRECTORY = "sound"

# The player always starts with 3 lives
INITIAL_LIVES = 3
# The player's score always starts at 0
INITIAL_SCORE = 0
# Initial level should always be 1
INITIAL_LEVEL = 1

# Pellets start out worth 10 points
INITIAL_PELLET_VALUE = 10
# 6 powerups are spawned at the start
INITIAL_POWERUP_COUNT = 6
# The powerup lasts 10 seconds at the start
INITIAL_POWERUP_TIME = 10
INITIAL_SCATTER_TIME = 7
INITIAL_CHASE_TIME = 15
# The movement speed starts at 1
INITIAL_SPEED_MULTIPLIER = 1

# These are the adjustments applied when the level advances
LIVES_BONUS = 1
SPEED_INCREMENT = 0.1
CHASE_INCREMENT = 1
PELLET_VALUE_INCREMENT = 10
SCATTER_DECREMENT = -1
POWERUP_TIME_DECREMENT = -1
POWERUP_COUNT_DECREMENT = -1

MAX_SPEED_MULTIPLIER = 2
MAX_PELLET_VALUE = 100
MIN_SCATTER_LENGTH = 0
MIN_POWERUP_LENGTH = 0
MIN_POWERUP_LIMIT = 0


# This is a separate widget because I intend to make HotrodGame into a layout
class PlayArea(Widget):
    """Widget for the gameplay area. Gameplay objects are children of this widget."""

    def start_game(self):
        """Start the game.

        This method begins the game.
        This method should be called when a game starts.
        That is, on first start, after a game over, or on
        a new level.
        """

        self.set_up_level()
        jingle = self.game.sounds['jingle']
        jingle.play()
        # Gameplay doesn't proceed until the jingle has finished
        jingle.bind(on_stop=self.start_updates)

    def set_up_level(self):
        """Set up the level and characters.

        This method initialises the generates the level and
        initialises the characters. It should be called when
        a new game or level starts.
        """

        self.generate_level()
        self.reset_characters()

    def generate_level(self):
        """Generate the level.

        This method procedurally generates the maze to be
        used for the level. It should be called when a new
        game or level starts.
        """

        seed = random.randint(0, sys.maxint)
        print seed
        random.seed(seed)
        self.game.level.generate_level()

    def reset_characters(self):
        """Completely reset the characters.

        This method ensures the characters' size, positions and
        certain modes are initialised, as well as resetting the
        activation timers, mode length and start position for the enemies.
        It should be called when a new game or level is started.
        """

        self.game.player.initialise()
        for enemy in self.game.enemies:
            enemy.reset_character()

    def initialise_characters(self):
        """Initialise the characters.

        This method ensures the characters' size, positions and
        certain modes are set to their initial values.
        It should be called when a new game or level is started, as well as
        when the player dies.
        """

        self.game.player.initialise()
        for enemy in self.game.enemies:
            enemy.initialise()

    def start_updates(self, event):
        """Start the game updating.

        This method begins the actual gameplay by setting the
        game_active property to True, as well as beginning
        the enemies' timers.. It should be called when a new game
        or level starts.
        """

        self.start_enemy_timers()
        self.game.game_active = True

    def update(self, dt):
        """Update the game state.

        This method should be called once every frame. It updates the
        state of the game, in this case, the characters' positions.
        """

        self.game.player.move()
        for enemy in self.game.enemies:
            if enemy.dead:
                enemy.retreat()
            else:
                enemy.move()

    def update_play_area(self, instance, value):
        """Ensure that game element sizes are correct.

        This Kivy event is triggered when window/level size changes to ensure
        that all elements of the play area are positioned and sized correctly
        """

        for column in self.game.level.cells:
            for cell in column:
                cell.update_cell()

        for enemy in self.game.enemies:
            enemy.update_character()
        self.game.player.update_character()

    def start_enemy_timers(self):
        """Start the timers for the enemies' mode changes and release.

        This method initialises the timers that count down
        to the enemies mode changes. This includes the timer
        between scatter/chase mode change, and the timer that
        determines when they are released. It should be called
        when a new game or level is started.

        Note: timers are started from this widget to ensure that they
        start after the intro music stops.
        """

        for enemy in self.game.enemies:
            enemy.start_scatter_timer()
            enemy.start_release_timer()

    def reset_after_death(self, event):
        """Reset the characters' positions and reset the scatter timer.

        This method both resets the characters' positions as well
        as resetting the enemies' chase mode change timers.
        It should only be called when the player has lost a life
        without it resulting in a game over.
        """

        self.initialise_characters()
        for enemy in self.game.enemies:
            enemy.start_scatter_timer()
        self.game.game_active = True


class HotrodGame(Widget):
    """Manage the game and application.

    This widget manages and controls the application.
    This widget has access to all major gameplay widgets, in addition
    to general game properties such as score and lives.
    Gameplay widgets access each other through this widget.
    """

    # References to game elements
    play_area = ObjectProperty(None)
    level = ObjectProperty(None)
    player = ObjectProperty(None)
    enemies = ListProperty()

    # Properties game keeps track of
    score = NumericProperty(INITIAL_SCORE)
    lives = NumericProperty(INITIAL_LIVES)
    level_number = NumericProperty(INITIAL_LEVEL)
    player_name = StringProperty()

    # Game properties
    pellet_count = NumericProperty()
    pellet_value = NumericProperty(INITIAL_PELLET_VALUE)

    # Difficulty modifiers
    powerup_limit = NumericProperty(INITIAL_POWERUP_COUNT)
    powerup_length = NumericProperty(INITIAL_POWERUP_TIME)
    scatter_length = NumericProperty(INITIAL_SCATTER_TIME)
    chase_length = NumericProperty(INITIAL_CHASE_TIME)
    speed_multiplier = NumericProperty(INITIAL_SPEED_MULTIPLIER)

    # GUI elements
    screens = ListProperty()
    game_over_screen = ObjectProperty(None)
    start_screen = ObjectProperty(None)
    login_screen = ObjectProperty(None)
    heads_up_display = ObjectProperty(None)

    # Dictionary containing all sounds used in the game
    sounds = ObjectProperty()

    # For managing game state
    game_active = BooleanProperty(False)

    def start(self):
        """Start the game.

        This method begins game progression.
        """
        self.remove_screens()
        self.play_area.start_game()

    def load_sounds(self):
        """Load the sounds used in the game.

        This method loads the sounds for use in the game and
        stores them in a dictionary for easy access.
        """

        self.sounds = {}
        # Dictionary keys correspond to filenames
        for file in os.listdir(SOUND_DIRECTORY):
            filename, extension = os.path.splitext(file)
            key = filename
            self.sounds[key] = SoundSDL2(source=(os.path.join(SOUND_DIRECTORY, file)))

    def on_touch_up(self, touch):
        """Detect player swipes and change character's next direction accordingly.

        This Kivy event detects swipes from the player and sets the player character's
        next direction to be the direction of the swipe.
        """

        if self.game_active:
            # Dividing by 10 means the swipe needs to be at least a 10th of the window
            # Move right if player swipes right
            if touch.pos[0] > touch.opos[0] + self.width/10:
                self.player.next_direction = direction.Direction.right
            # Move left if player swipes left
            if touch.pos[0] < touch.opos[0] - self.width/10:
                self.player.next_direction = direction.Direction.left
            # Move up is player swipes up
            if touch.pos[1] > touch.opos[1] + self.height/10:
                self.player.next_direction = direction.Direction.up
            # Move down if player swipes down
            if touch.pos[1] < touch.opos[1] - self.height/10:
                self.player.next_direction = direction.Direction.down

    def on_lives(self, instance, value):
        """Reset the play area if a life is lost or show game over screen if all are lost.

        Kivy event called when number of lives changes. The play area is reset upon
        losing a life. If all lives are lost, the game over screen is displayed.
        """

        # So that this doesn't happen when lives are reset or added after level
        if self.game_active:
            self.game_active = False

            if self.lives <= 0:
                game_over_sound = self.sounds['game_over']
                game_over_sound.bind(on_stop = self.show_game_over_screen)
                self.sounds['game_over'].play()
            else:
                death_sound = self.sounds['death']
                death_sound.bind(on_stop = self.play_area.reset_after_death)
                self.sounds['death'].play()

    def on_game_active(self, instance, value):
        """Start and stop game updates.

        This kivy event responds to changes in the boolean that
        states whether the game is active or not. If the game becomes
        active, updates are scheduled. If the game becomes inactive,
        updates are unscheduled.

        The game should deactivate in the following situations:
        Lose a life
        Getting a game over
        Advancing to the next level

        It should be restarted when:
        Next level has begun
        New game has begun
        After positions have reset after death
        """

        if self.game_active:
            Clock.schedule_interval(self.play_area.update, 1.0/FPS)
        else:
            Clock.unschedule(self.play_area.update)

    def show_screen(self, screen):
        """Show a given screen.

        This method displays the given screen. The screens must
        inherit from user_interface.Screen so that they have the
        set_size method.

        Arguments:
        screen - desired screen as a user_interface.Screen
        """

        screen.size = self.size
        screen.center = self.center
        self.add_widget(screen)
        self.bind(size=screen.set_size)
        self.screens.append(screen)

    def remove_screens(self):
        """Remove all screen widgets.

        This method removes all existing screens from
        visibility and unbinds them from the game's size.
        """

        for screen in self.screens:
            self.remove_widget(screen)
            self.unbind(size=screen.set_size)
            self.screens.remove(screen)

    def show_start_screen(self):
        """Show the start screen."""

        self.remove_screens()
        self.start_screen = user_interface.StartScreen()
        self.show_screen(self.start_screen)
        self.start_screen.start_button.bind(on_press=self.show_login_screen)

    def show_login_screen(self, event):
        """Show the login screen."""

        self.remove_screens()
        self.login_screen = user_interface.LoginScreen()
        self.show_screen(self.login_screen)
        self.login_screen.new_button.bind(on_press=self.add_user)

    def add_user(self, event):
        name = self.login_screen.new_name_text.text
        UrlRequest('http://bsccg02.ga.fal.io/adduser.py?player=' + name , self.check_added_user)
        self.login_screen.instruction_text.text = "Trying to add player..."

    def check_added_user(self, request, results):
        name = json.loads(results)
        if name is None:
            self.login_screen.instruction_text.text = "Invalid name!"
        else:
            self.player_name = name
            self.start()

    def show_game_over_screen(self, event):
        """Show the game over screen.

        This method shows the game over screen. The game over screen
        is displayed until the reset button is pressed.
        """

        self.game_over_screen = user_interface.GameOverScreen()
        self.show_screen(self.game_over_screen)
        self.game_over_screen.reset_button.bind(on_press=self.reset)

    def reset(self, event):
        """Reset the game after a game over.

        This method removes the game over widget and resets
        the score and lives count before restarting the game.
        """
        self.initialise_properties()
        self.start()

    def initialise_properties(self):
        self.level_number = INITIAL_LEVEL
        self.score = INITIAL_SCORE
        self.lives = INITIAL_LIVES
        self.pellet_value = INITIAL_PELLET_VALUE

        self.powerup_length = INITIAL_POWERUP_TIME
        self.scatter_length = INITIAL_SCATTER_TIME
        self.chase_length = INITIAL_CHASE_TIME
        self.speed_multiplier = INITIAL_SPEED_MULTIPLIER

    def advance_level(self):
        """Advance to the next level.

        This method stops the game and increases the
        level count and difficulty, before starting a
        new game based on these adjusted parameters.
        """

        self.game_active = False
        self.level_number += 1
        self.lives += 1
        self.start()

    def increase_difficulty(self):
        if self.pellet_value <= MAX_PELLET_VALUE - PELLET_VALUE_INCREMENT:
            self.pellet_value += PELLET_VALUE_INCREMENT
        if self.speed_multiplier <= MAX_SPEED_MULTIPLIER - SPEED_INCREMENT:
            self.speed_multiplier += SPEED_INCREMENT
        if self.scatter_length >= MIN_SCATTER_LENGTH - SCATTER_DECREMENT:
            self.scatter_length += SCATTER_DECREMENT
        if self.powerup_length >= MIN_POWERUP_LENGTH - POWERUP_TIME_DECREMENT:
            self.powerup_length += POWERUP_TIME_DECREMENT
        if self.powerup_limit >= MIN_POWERUP_LIMIT - POWERUP_COUNT_DECREMENT:
            self.powerup_limit += POWERUP_COUNT_DECREMENT

        self.chase_length += CHASE_INCREMENT

        print "chase: " + str(self.chase_length)
        print "scatter: " + str(self.scatter_length)
        print "speed:" + str(self.speed_multiplier)
        print "power: " + str(self.powerup_length)

    def on_level_number(self, instance, value):
        if self.level_number != 1:
            self.increase_difficulty()

    def on_pellet_count(self, instance, value):
        if self.pellet_count == 0:
            if self.game_active:
                self.advance_level()


class HotrodApp(App):
    # game is property so that it can be referred to
    # outside of build()
    game = ObjectProperty(None)

    def build(self):
     #   Config.set('graphics', 'fullscreen', 'auto')
        self.game = HotrodGame()
        return self.game

    def on_start(self):
        # Called here rather than in build() so that size is correct
        self.game.load_sounds()
        self.game.show_start_screen()


if __name__ == '__main__':
    HotrodApp().run()