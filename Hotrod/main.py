__author__ = 'Harriet'

import random

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty, ReferenceListProperty, ListProperty, BooleanProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.config import Config

import direction

class PlayArea(Widget):
    player = ObjectProperty(None)

    columns = NumericProperty(10)
    rows = NumericProperty(10)

    cells = ListProperty()
    cell_size = ObjectProperty()

    padding = NumericProperty()

    def generate_level(self):

        for x in range(self.columns):
            for y in range(self.rows):
               self.create_cell((x, y))
        for cell in self.cells:
            self.add_widget(cell)
        self.player.size = self.cells[0].interior
        self.player.center = self.cells[0].center

    def create_cell(self, coords):
        """Create a Cell at provided grid coordinates"""
        cell = Cell()
        cell.size = self.cell_size
        cell.pos = self.get_cell_coords(coords, cell.size)
        self.cells.append(cell)

    def get_cell_coords(self, (x, y), (width, height)):
        """Convert grid coordinates to window coordinates"""
        return ((width * x + self.padding, height * y))

    def update(self):
        self.player.move()
        #
        # for cell in self.cells:
        #     for wall in cell.walls:
        #         if wall.collide_widget(self.player):
        #             self.player.velocity = 0, 0

        if (self.player.y <= 0 or self.player.top >= self.top):
            self.player.velocity_y = 0
        if (self.player.x <= self.x or self.player.right >= self.right):
            self.player.velocity_x = 0

    def on_touch_up(self, touch):
        # Move right if player swipes right
        if touch.pos[0] > touch.opos[0] + self.width/10:
            self.player.move_direction = direction.Direction.right
        # Move left if player swipes left
        if touch.pos[0] < touch.opos[0] - self.width/10:
            self.player.move_direction = direction.Direction.left
        # Move up is player swipes up
        if touch.pos[1] > touch.opos[1] + self.height/10:
            self.player.move_direction = direction.Direction.up
        # Move down if player swipes down
        if touch.pos[1] < touch.opos[1] - self.height/10:
            self.player.move_direction = direction.Direction.down
        self.player.color = (random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1))


class Wall(Widget):
    angle = NumericProperty(0)


class Cell(Widget):
    sides = NumericProperty(4)
    wall_thickness = NumericProperty(0.1)
    interior = ListProperty()

    left_wall = ObjectProperty(None)
    right_wall = ObjectProperty(None)
    top_wall = ObjectProperty(None)
    bottom_wall = ObjectProperty(None)

    walls = ListProperty()


class PlayerBeetle(Widget):
    speed = NumericProperty()
    color = ObjectProperty((1, 1, 1))

    move_direction = ObjectProperty(direction.Direction.right)

    can_move = BooleanProperty(True)

    def move(self):
        self.pos = Vector(self.move_direction.value[0] * self.speed,
                          self.move_direction.value[1] * self.speed) + self.pos


class HotrodGame(Widget):
    play_area = ObjectProperty(None)


    def start(self):
        self.play_area.generate_level()

    def update(self, dt):
        self.play_area.update()


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