
from enum import Enum

from kivy.uix.widget import Widget
from kivy.properties import NumericProperty
from kivy.properties import ReferenceListProperty
from kivy.properties import ObjectProperty

class Pellet(Widget):
    coordinates_x = NumericProperty(0)
    coordinates_y = NumericProperty(0)
    coordinates = ReferenceListProperty(coordinates_x, coordinates_y)

    type = ObjectProperty()
    power_probability = NumericProperty(0.05)

    color = ObjectProperty((0, 0, 0))

    def update_pellet_widget(self):
        """Set up pellet properties.

        This method sets up the pellet size, color, and position depending
        on its type. It should be called when the pellet type changes or
        when the window size changes.
        """
        if self.type == PelletType.normal:
            self.width = self.parent.width / 10
            self.height = self.parent.height / 10
            self.color = (0.9, 0.9, 0)

        elif self.type == PelletType.power:
            self.width = self.parent.width / 5
            self.height = self.parent.height / 5
            self.color = (0.9, 0, 0)
        self.center = self.parent.center

    def on_type(self, instance, value):
        """Update the pellet if its type changes

        This is kivy event called when the pellet type changes. It causes the
        pellet widget's properties to be updated.
        """
        self.update_pellet_widget()

class PelletType(Enum):
    normal = 0
    power = 1
