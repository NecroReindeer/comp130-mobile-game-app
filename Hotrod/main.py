import random
import sys

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.properties import NumericProperty
from kivy.properties import BooleanProperty
from kivy.properties import ListProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.config import Config
from kivy.uix.button import Button

import direction
import level
import level_cell
import character
import user_interface

FPS = 60

INITIAL_LIVES = 3
INITIAL_SCORE = 0

# This is a separate widget because I intend to make HotrodGame into a layout
class PlayArea(Widget):
    """Widget for the gameplay area. Gameplay objects are children of this widget."""

    def start_game(self):
        self.generate_level()
        self.initialise_characters()

    def generate_level(self):
        seed = random.randint(0, sys.maxint)
        print seed
        random.seed(seed)
        self.game.level.generate_level()

    def initialise_characters(self):
        self.game.player.initialise((0, 0))
        self.game.red_enemy.initialise((self.game.level.columns-1, self.game.level.rows - 1))
        self.game.pink_enemy.initialise((0, self.game.level.rows-1))
        self.game.blue_enemy.initialise((self.game.level.columns-1, 0))
        self.game.orange_enemy.initialise((5, 5))

        for enemy in self.game.enemies:
            Clock.schedule_once(enemy.change_mode, enemy.mode_change_timer)

    def update_play_area(self, instance, value):
        """Kivy event triggered when level size changes to ensure that all
        elements of the play area are positioned and sized correctly"""
        for column in self.game.level.cells:
            for cell in column:
                cell.update_cell()

        for pellet in self.game.level.pellets:
            pellet.update_pellet()

        for enemy in self.game.enemies:
            enemy.update_character()
        self.game.player.update_character()


class HotrodGame(Widget):
    """Widget for controlling the game and application. Widgets can access
    each other through this widget.
    This widget has access to each main gameplay widget, general
    properties such as scores, and settings that affect the game.
    """
    play_area = ObjectProperty(None)
    level = ObjectProperty(None)

    player = ObjectProperty(None)

    enemies = ListProperty()
    score = NumericProperty(INITIAL_SCORE)
    lives = NumericProperty(INITIAL_LIVES)

    # GUI elements so that they can be referred to in
    # multiple methods
    game_over_screen = ObjectProperty(None)

    def start(self):
        self.play_area.start_game()
        Clock.schedule_interval(self.update, 1.0/FPS)

    def update(self, dt):
        self.player.move()
        for enemy in self.enemies:
            enemy.move()
        self.level.check_pellet_collisions()


    def on_touch_up(self, touch):
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
        """Kivy event called when number of lives changes"""
        self.play_area.initialise_characters()
        if self.lives <= 0:
            Clock.unschedule(self.update)
            self.show_game_over_screen()
            # Stop the game

    def show_game_over_screen(self):
        self.game_over_screen = user_interface.GameOverScreen()
        self.game_over_screen.size = self.size
        self.game_over_screen.center = self.center
        self.add_widget(self.game_over_screen)
        self.game_over_screen.reset_button.bind(on_press=self.reset)
        self.bind(size=self.game_over_screen.set_size)

    def reset(self, event):
        self.remove_widget(self.game_over_screen)
        self.unbind(size=self.game_over_screen.set_size)
        self.score = INITIAL_SCORE
        self.lives = INITIAL_LIVES
        self.start()


class HotrodApp(App):
    # game is property so that it can be referred to
    # outside of build()
    game = ObjectProperty(None)

    def build(self):
     #   Config.set('graphics', 'fullscreen', 'auto')
        self.game = HotrodGame()
        return self.game

    def on_start(self):
        # Called here rather than in build() so that
        # size is correct
        self.game.start()


if __name__ == '__main__':
    HotrodApp().run()