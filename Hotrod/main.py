__author__ = 'Harriet'

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty, ReferenceListProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.uix.floatlayout import  FloatLayout

class PlayerBeetle(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

class HotrodGame(Widget):
    player = ObjectProperty(None)

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


class HotrodApp(App):
    def build(self):
        game = HotrodGame()
        Clock.schedule_interval(game.update, 1.0/60.0)
        return game


if __name__ == '__main__':
    HotrodApp().run()