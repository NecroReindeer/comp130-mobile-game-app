__author__ = 'Harriet'

import random

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

class PlayArea(Widget):
    player = ObjectProperty(None)
    level = ObjectProperty(None)

    def generate_level(self):
        self.level.generate_level()
        self.player.size = self.level.cells[0][0].interior
        self.player.center = self.level.cells[0][0].center

    def update(self):
        self.player.move()
        self.level.check_pellet_collisions()


class HotrodGame(Widget):
    play_area = ObjectProperty(None)
    # Allow game controller access to player widget
    player = ObjectProperty(None)
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
        self.player.color = (random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1))


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