__author__ = 'Hat'

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget


class GameOverScreen(FloatLayout):
    def set_size(self, instance, value):
        self.size = self.parent.size
        self.center = self.parent.center

class HeadsUpDisplay(FloatLayout):
    def set_size(self, instance, value):
        self.size = self.parent.size
        self.center = self.parent.center

        self.score_label.text_size = self.width, None