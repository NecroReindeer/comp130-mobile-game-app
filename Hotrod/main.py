__author__ = 'Harriet'

import random
import sys

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty, ReferenceListProperty, ListProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.config import Config

import direction
import level
import level_cell
import character

# This is a separate widget because I intend to make HotrodGame into a layout
class PlayArea(Widget):
    """Widget for the gameplay area. Gameplay objects are children of this widget."""

    def generate_level(self):
        seed = random.randint(0, sys.maxint)
    #   seed = 188100911
        print seed
        random.seed(seed)
        self.game.level.generate_level()
        self.game.red_enemy.size = self.game.level.cells[0][0].interior
        self.game.red_enemy.center = self.game.level.cells[self.game.level.columns - 1][self.game.level.rows - 1].center
        self.game.player.size = self.game.level.cells[0][0].interior
        self.game.player.center = self.game.level.cells[0][0].center

    def update(self):
        self.game.player.move()
        self.game.red_enemy.move()
        self.game.level.check_pellet_collisions()


class HotrodGame(Widget):
    """Widget for controlling the game and application. Widgets can access
    each other through this widget.
    This widget has access to each main gameplay widget, general
    properties such as scores, and settings that affect the game.
    """
    play_area = ObjectProperty(None)
    level = ObjectProperty(None)

    player = ObjectProperty(None)
    red_enemy = ObjectProperty(None)

    score = NumericProperty(0)

    def start(self):
        self.play_area.generate_level()

    def update(self, dt):
        self.play_area.update()

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


class HotrodApp(App):
    # game is property so that it can be referred to
    # outside of build()
    game = ObjectProperty(None)

    def build(self):
        Config.set('graphics', 'fullscreen', 'auto')
        self.game = HotrodGame()
        Clock.schedule_interval(self.game.update, 1.0/60.0)
        return self.game

    def on_start(self):
        # Called here rather than in build() so that
        # size is correct
        self.game.start()



if __name__ == '__main__':
    HotrodApp().run()