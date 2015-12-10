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
from kivy.uix.floatlayout import FloatLayout

import direction
import level
import level_cell
import character

FPS = 60

INITIAL_LIVES = 3
INITIAL_SCORE = 0

# This is a separate widget because I intend to make HotrodGame into a layout
class PlayArea(Widget):
    """Widget for the gameplay area. Gameplay objects are children of this widget."""

    def start_game(self):
        print self.pos
        self.generate_level()
        print self.game.level.cells[0][0].pos
        self.initialise_characters()

    def generate_level(self):
        seed = random.randint(0, sys.maxint)
    #   seed = 188100911
      #  seed = 2122483418
        print seed
        random.seed(seed)
        self.game.level.generate_level()

    def initialise_characters(self):
        self.game.player.initialise((0, 0))
        self.game.red_enemy.initialise((self.game.level.columns-1, self.game.level.rows - 1))
        self.game.pink_enemy.initialise((0, self.game.level.rows-1))
        self.game.blue_enemy.initialise((self.game.level.columns-1, 0))
        self.game.orange_enemy.initialise((5, 5))


class HotrodGame(FloatLayout):
    """Widget for controlling the game and application. Widgets can access
    each other through this widget.
    This widget has access to each main gameplay widget, general
    properties such as scores, and settings that affect the game.
    """
    game_in_progress = BooleanProperty(False)
    play_area = ObjectProperty(None)
    level = ObjectProperty(None)

    player = ObjectProperty(None)

    enemies = ListProperty()
    score = NumericProperty(INITIAL_SCORE)
    lives = NumericProperty(INITIAL_LIVES)

    def start(self):
        self.play_area.start_game()
        Clock.schedule_interval(self.update, 1.0/FPS)
        self.game_in_progress = True


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
            self.reset()
            Clock.unschedule(self.update)
            self.start()

    def reset(self):
        self.score = INITIAL_SCORE
        self.lives = INITIAL_LIVES


class HotrodApp(App):
    # game is property so that it can be referred to
    # outside of build()
    game = ObjectProperty(None)

    def build(self):
      #  Config.set('graphics', 'fullscreen', 'auto')
        self.game = HotrodGame()
        return self.game

    def on_start(self):
        # Called here rather than in build() so that
        # size is correct
        self.game.start()


if __name__ == '__main__':
    HotrodApp().run()