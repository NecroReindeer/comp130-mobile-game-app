"""Contain classes for managing the game application.

This file contains classes that are used for managing the
game application. Running this file will run the app.

Classes:
HotrodApp(App) -- Kivy App widget
HotrodGame(Widget) -- root game widget
PlayArea(Widget) -- widget for the gameplay area
"""

# Standard Python libraries
import json
import random
import os
import sys

# Kivy modules
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
from kivy.core.audio import SoundLoader
from kivy.core.audio.audio_sdl2 import SoundSDL2
from kivy.network.urlrequest import UrlRequest

# Own modules
import direction
import level
import level_cell
import character
import server
import user_interface


# Number of frames per second the game should run at
FPS = 60
# The relative location of the game's sound files
SOUND_DIRECTORY = "sound"

# The values specified below were chosen to tune the game's difficulty

# These are initial values generic properties that the game keeps track of
# Number of lives the player starts with
INITIAL_LIVES = 3
# The initial score the player starts with
INITIAL_SCORE = 0
# The level number of the initial level
INITIAL_LEVEL = 1

# These are initial values of properties that modify the games's difficulty/rewards
# The points that kills add on the first level
INITIAL_KILL_VALUE = 100
# The points that pellets add on the first level
INITIAL_PELLET_VALUE = 10
# The number of powerups spawned on the first level
INITIAL_POWERUP_LIMIT = 6
# The length of time in seconds powerups last on the first level
INITIAL_POWERUP_TIME = 10
# The number of consecutive seconds enemies target the player for
INITIAL_CHASE_TIME = 15
# The number of consecutive seconds enemies stop targeting the player
INITIAL_SCATTER_TIME = 7
# The movement speed of characters on the first level
INITIAL_SPEED_MULTIPLIER = 1

# These are the adjustments applied to the respective property when the level advances
LIVES_BONUS = 1
SPEED_INCREMENT = 0.1
CHASE_INCREMENT = 1
PELLET_VALUE_INCREMENT = 10
KILL_VALUE_INCREMENT = 100
SCATTER_DECREMENT = -1
POWERUP_TIME_DECREMENT = -1
POWERUP_LIMIT_DECREMENT = -1

# These are the maximum/minimum values the adjusted properties can take
MAX_SPEED_MULTIPLIER = 2
MAX_PELLET_VALUE = 100
MIN_SCATTER_LENGTH = 0
MIN_POWERUP_LENGTH = 0
MIN_POWERUP_LIMIT = 0


class PlayArea(Widget):

    """Store methods related to the mechanics and visualisation of the game.

    This widget represents the gameplay area. The gameplay objects are children of this widget.
    This class handles anything relating to the graphical representation of the game and the
    mechanics of the game. This includes level generation, movement updates, and character initialisation.

    Public methods:
    start_game -- begins the game

    Kivy Events:
    update -- updates the game/moves the characters
    reset_after_death -- restarts the level after player dies
    update_play_area -- ensures play area is sized correctly
    check_character_collisions -- check if player has collided with enemy
    """

    def start_game(self):
        """Start the game.

        This method begins the game.
        This method should be called when a game first starts,
        after a game over, or on a new level.
        """

        self.__set_up_level()
        jingle = self.game.sounds['jingle']
        jingle.play()
        # Gameplay doesn't proceed until the jingle has finished
        jingle.bind(on_stop=self.__start_updates)

    def __set_up_level(self):
        """Set up the level and characters.

        This method initialises the generates the level and
        resets the characters. It should be called when
        a new game or level starts.
        """

        self.__generate_level()
        self.__reset_characters()

    def __generate_level(self):
        """Generate the level.

        This method procedurally generates the maze to be
        used for the level. It should be called when a new
        game or level starts.
        """

        seed = random.randint(0, sys.maxint)
        # Print seed for debugging purposes
        print seed
        random.seed(seed)
        self.game.level.generate_level()

    def __reset_characters(self):
        """Completely reset the characters.

        This method ensures the characters' size, positions and
        certain modes are initialised, as well as resetting the
        activation timers, mode length and start position for the enemies.
        It should be called only when a new game or level is started.
        """

        self.game.player.initialise()
        for enemy in self.game.enemies:
            enemy.reset_character()

    def __initialise_characters(self):
        """Initialise the characters.

        This method ensures the characters' size, positions and
        certain modes are set to their initial values.
        It should be called when a new game or level is started, as well as
        when the player dies.
        """

        self.game.player.initialise()
        for enemy in self.game.enemies:
            enemy.initialise()

    def __start_updates(self, event):
        """Start the game's updates.

        This method begins the actual gameplay by setting the
        game_active property to True, as well as beginning
        the enemies' timers. It should be called when a new game
        or level starts.
        This method is triggered by a Kivy event so that the game
        begins after the jingle stops playing.
        """

        self.__start_enemy_timers()
        self.game.game_active = True

    def __start_enemy_timers(self):
        """Start the timers for the enemies' mode changes and release.

        This method initialises the timers that count down
        to the enemies mode changes. This includes the timer
        between scatter/chase mode change, and the timer that
        determines when they are released. It should be called
        when a new game or level is started.

        Note: timers are started from this method to ensure that they
        start after the intro music stops.
        """

        for enemy in self.game.enemies:
            enemy.start_mode_change_timer()
            enemy.start_activation_timer()

    def update(self, dt):
        """Update the game state.

        This method should be scheduled on the Kivy clock to be called once every frame.
        It updates the state of the game.
        (currently, in this case, only the characters' positions)
        """

        self.game.player.move()
        for enemy in self.game.enemies:
            enemy.move()

    def reset_after_death(self, event):
        """Reset the characters' positions and reset the scatter timer.

        This method both resets the characters' positions as well
        as resetting the enemies' chase mode change timers.
        It should only be called when the player has lost a life
        without it resulting in a game over.
        This is a Kivy property event binding so that it happens after
        the death jingle has finished playing.
        """

        self.__initialise_characters()
        for enemy in self.game.enemies:
            enemy.start_mode_change_timer()
        self.game.game_active = True

    def update_play_area_size(self, instance, value):
        """Ensure that game element sizes are correct.

        This Kivy event is triggered when window/level size changes to ensure
        that all elements of the play area are positioned and sized correctly.
        """

        for column in self.game.level.cells:
            for cell in column:
                cell.update_cell_size()

        for enemy in self.game.enemies:
            enemy.update_character_size()
        self.game.player.update_character_size()

    def check_character_collisions(self, instance, value):
        """Check for character collisions.

        This method checks if the player is in the same grid position as an
        enemy. If so, the player is set to dead. If the player has a power-up
        and the enemy is frightened, the enemy is set to dead instead.
        It is a Kivy property binding tied to the characters' grid positions.
        """

        for enemy in self.game.enemies:
            if enemy.grid_position == self.game.player.grid_position:
                if self.game.player.powered_up and enemy.frightened:
                    enemy.kill_character()
                elif not enemy.dead:
                    self.game.player.kill_character()


class HotrodGame(Widget):

    """Manage the game and application.

    This widget manages and controls the application.
    This widget has access to all major gameplay widgets, in addition
    to general game properties such as score and lives.
    This widget contains methods that facilitate the menu screens and
    application flow, as well as reading input from the user.
    It stores general information relating to the game that is of
    use to the user, such as score and lives.
    Gameplay widgets access each other through this widget.

    Public methods:
    show_start_screen -- displays the start screen
    load_sounds -- loads the game's sounds

    Kivy events:
    on_pellet_count -- checks if level has been completed
    on_level_number -- advances to the next level
    on_lives -- restarts level/ends game when player loses life
    on_game_active -- starts and stops updates
    on_touch_up -- built in Kivy event that detects touch from user

    Kivy properties:
    score -- NumericProperty to track player's score
    lives -- NumericProperty to track player's remaining lives
    level_number -- NumericProperty to track the level number
    player_name -- StringProperty to store the player's name
    pellet_count -- NumericProperty for counting how many pellets remain
    powerup_limit -- NumericProperty storing the number of powerups that can spawn
    powerup_length -- NumericProperty storing the number of seconds a powerup lasts
    scatter_length -- NumericProperty storing the number of seconds the enemies scatter
    chase_length -- NumericProperty storing the number of seconds the enemies target the player
    speed_multiplier -- NumericProperty storing the value the character's base speed will be multiplied by
    pellet_value -- NumericProperty storing the number of points pellets are worth
    kill_value -- NumericProperty storing the number of points kills are worth
    screens -- ListProperty to track screens that are currently displayed
    game_over_screen -- ObjectProperty to store a reference to the game over screen
    start_screen -- ObjectProperty to store a reference to the start screen
    login_screen -- ObjectProperty to store a reference to the login screen
    sounds -- ObjectProperty to store a dictionary of sound assets for the game
    game_active -- BooleanProperty to keep track of whether the game is in progress
    enemies -- ListProperty to store a list of all the enemies (kv file)
    hud_width -- NumericProperty to store the width of the HUD (kv file)
    """

    # General properties game keeps track of
    score = NumericProperty(INITIAL_SCORE)
    lives = NumericProperty(INITIAL_LIVES)
    level_number = NumericProperty(INITIAL_LEVEL)
    player_name = StringProperty()
    # Pellet counter should start counting from 0
    pellet_count = NumericProperty(0)


    # Game properties and difficulty modifiers
    powerup_limit = NumericProperty(INITIAL_POWERUP_LIMIT)
    powerup_length = NumericProperty(INITIAL_POWERUP_TIME)
    scatter_length = NumericProperty(INITIAL_SCATTER_TIME)
    chase_length = NumericProperty(INITIAL_CHASE_TIME)
    speed_multiplier = NumericProperty(INITIAL_SPEED_MULTIPLIER)
    pellet_value = NumericProperty(INITIAL_PELLET_VALUE)
    kill_value = NumericProperty(INITIAL_KILL_VALUE)

    # GUI elements
    screens = ListProperty()
    game_over_screen = ObjectProperty(None)
    start_screen = ObjectProperty(None)
    login_screen = ObjectProperty(None)

    # Dictionary containing all sounds used in the game
    sounds = ObjectProperty()

    # For managing game state
    game_active = BooleanProperty(False)

    def show_start_screen(self):
        """Show the start screen.

        This method shows the start screen and plays the title music.
        It also binds the start screen's button to show the login
        screen. It ensures that no other screens are displayed by
        removing them all first.
        """

        self.sounds['title'].play()
        self.__remove_screens()
        self.start_screen = user_interface.StartScreen()
        self.__show_screen(self.start_screen)
        self.start_screen.start_button.bind(on_press=self.__show_login_screen)

    def load_sounds(self):
        """Load the sounds used in the game.

        This method loads the sounds for use in the game and
        stores them in a dictionary for easy access.
        """

        self.sounds = {}
        # Dictionary keys correspond to filenames
        for file in os.listdir(SOUND_DIRECTORY):
            filename, extension = os.path.splitext(file)
            dictionary_key = filename
            self.sounds[dictionary_key] = SoundSDL2(source=(os.path.join(SOUND_DIRECTORY, file)))

        self.sounds['title'].loop = True
        self.sounds['frightened'].loop = True

    def __start_game(self):
        """Start the game.

        This method begins game progression. It ensures that
        all screens are removed and the title music is stopped,
        before triggering the play area to start the game.
        """

        self.__remove_screens()
        self.sounds['title'].stop()
        self.play_area.start_game()

    def __reset(self, event):
        """Reset the game after a game over.

        This method initialises the game's properties
        and then restarts the game.
        """

        self.__initialise_properties()
        self.__start_game()

    def __initialise_properties(self):
        """Initialise the game's properties.

        This method sets all of the game's properties to their
        initial values, as defined by the corresponding constants.
        """

        self.level_number = INITIAL_LEVEL
        self.score = INITIAL_SCORE
        self.lives = INITIAL_LIVES
        self.pellet_value = INITIAL_PELLET_VALUE
        self.kill_value = INITIAL_KILL_VALUE

        self.powerup_length = INITIAL_POWERUP_TIME
        self.scatter_length = INITIAL_SCATTER_TIME
        self.chase_length = INITIAL_CHASE_TIME
        self.speed_multiplier = INITIAL_SPEED_MULTIPLIER

        # Ensure pellet counter starts at 0
        self.pellet_count = 0

    def __advance_level(self):
        """Advance to the next level.

        This method stops the game and increases the
        level number and difficulty, before starting a
        new game based on these adjusted parameters.
        """

        self.game_active = False
        # Increase level number and lives by 1
        self.level_number += 1
        self.lives += 1
        self.__start_game()

    def __increase_difficulty(self):
        """Increase the difficulty.

        This method increases the difficulty by adjusting the values
        of the relevant properties by the defined increment, until they
        will exceed their maximum or minimum values.
        """

        if self.speed_multiplier <= MAX_SPEED_MULTIPLIER - SPEED_INCREMENT:
            self.speed_multiplier += SPEED_INCREMENT
        if self.scatter_length >= MIN_SCATTER_LENGTH - SCATTER_DECREMENT:
            self.scatter_length += SCATTER_DECREMENT
        if self.powerup_length >= MIN_POWERUP_LENGTH - POWERUP_TIME_DECREMENT:
            self.powerup_length += POWERUP_TIME_DECREMENT
        if self.powerup_limit >= MIN_POWERUP_LIMIT - POWERUP_LIMIT_DECREMENT:
            self.powerup_limit += POWERUP_LIMIT_DECREMENT

        self.chase_length += CHASE_INCREMENT
        self.pellet_value += PELLET_VALUE_INCREMENT
        self.kill_value += KILL_VALUE_INCREMENT

    def __show_screen(self, screen):
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

    def __remove_screens(self):
        """Remove all screen widgets.

        This method removes all existing screens from
        visibility and unbinds them from the game's size.
        """

        for screen in self.screens:
            self.remove_widget(screen)
            self.unbind(size=screen.set_size)
            self.screens.remove(screen)

    def __show_login_screen(self, event):
        """Show the login screen.

        This method is triggered by a Kivy event.
        This method shows the login screen and binds the buttons to
        the appropriate add user/get user methods.
        It ensures that no other screens are displaying by
        removing them all first.
        """

        self.__remove_screens()
        self.login_screen = user_interface.LoginScreen()
        self.__show_screen(self.login_screen)
        self.login_screen.new_button.bind(on_press=self.__add_new_user)
        self.login_screen.existing_button.bind(on_press=self.__get_existing_user)

    def __show_game_over_screen(self, event):
        """Show the game over screen and high scores.

        This method shows the game over screen along with the
        high scores for the level.
        The game over screen is displayed until the reset button
        is pressed.
        """

        self.sounds['title'].play()
        self.game_over_screen = user_interface.GameOverScreen()
        self.__show_screen(self.game_over_screen)
        self.game_over_screen.show_final_score(self.score)
        self.game_over_screen.show_best_score(self.player_name, self.level_number, self.score)
        self.game_over_screen.show_high_scores(self.level_number)
        self.game_over_screen.reset_button.bind(on_press=self.__reset)

    def __add_new_user(self, event):
        """Add a new user to the game.

        This Kivy property bind event adds a new user to the
        database and attempts to begin the game.
        """

        name = self.login_screen.name_text.text
        UrlRequest('http://bsccg02.ga.fal.io/adduser.py?player=' + name, self.__check_user)
        self.login_screen.instruction_text.text = "Adding player..."
        self.login_screen.new_button.disabled = True

    def __get_existing_user(self, event):
        """Find an existing user in the database.

        This Kivy property bind event sees if the user exists in
        the database and attempts to begin the game.
        """

        name = self.login_screen.name_text.text
        UrlRequest('http://bsccg02.ga.fal.io/getuser.py?player=' + name, self.__check_user)
        self.login_screen.instruction_text.text = "Logging in..."
        self.login_screen.existing_button.disabled = True

    def __check_user(self, request, results):
        """Check if the user login/addition was successful.

        This method checks if the user was added successfully or if
        an existing player logged in successfully. If it was
        successful, it begins the game.
        """

        name = json.loads(results)
        if name is None:
            self.login_screen.instruction_text.text = "Invalid name!"
            self.login_screen.new_button.disabled = False
            self.login_screen.existing_button.disabled = False
        else:
            self.player_name = name
            self.__start_game()

    def on_level_number(self, instance, value):
        """Increase the difficulty after the level advances.

        This Kivy event is called when the level number changes.
        If the level number is after level 1, the difficulty gets
        increased.
        """

        # After level 1, so that difficulty doesn't increase on start
        if self.level_number != 1:
            self.__increase_difficulty()

    def on_pellet_count(self, instance, value):
        """Advance the level when pellets are all gone.

        This Kivy event is called when the pellet count changes.
        If the pellet count gets to 0, the level advances.
        """

        # If there are no pellets left
        if self.pellet_count == 0:
            if self.game_active:
                self.__advance_level()

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
        The restarted level or game over screen isn't shown until the death music
        has stopped.
        """

        # So that this doesn't happen when lives are reset or added after level
        if self.game_active:
            self.game_active = False

            if self.lives <= 0:
                game_over_sound = self.sounds['game_over']
                game_over_sound.bind(on_stop=self.__show_game_over_screen)
                self.sounds['game_over'].play()
            else:
                death_sound = self.sounds['death']
                death_sound.bind(on_stop=self.play_area.reset_after_death)
                self.sounds['death'].play()

    def on_game_active(self, instance, value):
        """Start and stop game updates.

        This Kivy event responds to changes in the boolean that
        states whether the game is active or not. If the game becomes
        active, updates are scheduled. If the game becomes inactive,
        updates are unscheduled.

        The game should deactivate in the following situations:
        Lose a life, getting a game over, or advancing to the next level
        It should be restarted when:
        Next level has begun, new game has begun, or after positions have reset after death
        """

        if self.game_active:
            Clock.schedule_interval(self.play_area.update, 1.0/FPS)
        else:
            Clock.unschedule(self.play_area.update)


class HotrodApp(App):
    # game is property so that it can be referred to outside of build()
    game = ObjectProperty(None)

    def build(self):
        #Config.set('graphics', 'fullscreen', 'auto')
        self.game = HotrodGame()
        return self.game

    def on_start(self):
        # Called here rather than in build() so that size is correct
        self.game.load_sounds()
        self.game.show_start_screen()


if __name__ == '__main__':
    HotrodApp().run()