__author__ = 'Harriet'

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty, ReferenceListProperty, ListProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.config import Config

import random

class PlayArea(Widget):
    columns = NumericProperty(10)
    rows = NumericProperty(10)
    cells = ListProperty([])
    padding = NumericProperty()

    def generate_level(self):
        for x in range(self.columns):
            for y in range(self.rows):
               self.create_cell((x, y))
        for cell in self.cells:
            self.add_widget(cell)

    def create_cell(self, coords):
        """Create a cell at provided grid coordinates"""
        cell = Cell()
        cell.height = self.height/self.rows
        cell.width = cell.height
        cell.pos = self.get_cell_coords(coords, cell.size)
        self.cells.append(cell)

    def get_cell_coords(self, (x, y), (width, height)):
        """Convert grid coordinates to pixel coordinates"""
        return ((width * x + self.padding, height * y))


class Wall(Widget):
    pass


class Cell(Widget):
    sides = NumericProperty(4)
    wall_thickness = NumericProperty(0.1)

    left_wall = ObjectProperty(None)
    right_wall = ObjectProperty(None)
    top_wall = ObjectProperty(None)
    bottom_wall = ObjectProperty(None)


class PlayerBeetle(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    color = ObjectProperty((1, 1, 1))

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos


class HotrodGame(Widget):
    player = ObjectProperty(None)
    play_area = ObjectProperty(None)

    def start(self):
        self.play_area.generate_level()

    def update(self, dt):
        self.player.move()

        if (self.player.y <= 0 or self.player.top >= self.top):
            self.player.velocity_y = 0
        if (self.player.x <= self.x or self.player.right >= self.width):
            self.player.velocity_x = 0

    def on_touch_up(self, touch):
        # Move right if player swipes right
        if touch.pos[0] > touch.opos[0] + self.width/10:
            self.player.velocity_x = 5
            self.player.velocity_y = 0
        # Move left if player swipes left
        if touch.pos[0] < touch.opos[0] - self.width/10:
            self.player.velocity_x = -5
            self.player.velocity_y = 0
        # Move up is player swipes up
        if touch.pos[1] > touch.opos[1] + self.height/10:
            self.player.velocity_x = 0
            self.player.velocity_y = 5
        # Move down if player swipes down
        if touch.pos[1] < touch.opos[1] - self.height/10:
            self.player.velocity_x = 0
            self.player.velocity_y = -5
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