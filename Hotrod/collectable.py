"""Contain classes relating to collectables.

This module contains classes that relate to objects that
the player can collect.

Classes:
Pellet(Widget) -- class for all pellets
PelletType(Enum) -- enum for storing the type of a pellet
"""


# Kivy Modules
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty
from kivy.properties import ReferenceListProperty
from kivy.properties import ObjectProperty

# Other modules
from enum import Enum


class Pellet(Widget):
    """Contain information about the pellet widget.

    This class primarily stores information about the pellet
    widget, such as its type and colour. It also stores methods for
    ensuring that the pellet is displayed correctly.

    Public Methods:
    update_pellet_widget -- ensure the pellet's size and colour is correct

    Kivy Events:
    on_type -- updates the pellet widget when the type changes

    Kivy Properties:
    type -- ObjectProperty to store enum representing the pellet's type
    color -- ObjectProperty to store the colour of the pellet. (kv file)
    """

    type = ObjectProperty()

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

        This is a Kivy event called when the pellet type changes. It causes the
        pellet widget's properties to be updated.
        """

        self.update_pellet_widget()


class PelletType(Enum):
    """Store enumerations for pellet types

    This is an enum to represent the different types of pellet.
    """

    normal = 0
    power = 1
