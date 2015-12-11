
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty
from kivy.properties import ReferenceListProperty

class Pellet(Widget):
    coordinates_x = NumericProperty(0)
    coordinates_y = NumericProperty(0)
    coordinates = ReferenceListProperty(coordinates_x, coordinates_y)

    def update_pellet(self):
        cell = self.parent.get_cell(self.coordinates)
        self.width = cell.width / 10
        self.height = cell.height / 10
        self.center = cell.center