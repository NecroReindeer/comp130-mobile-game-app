__author__ = 'Harriet'

import random

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty, ReferenceListProperty, ListProperty, BooleanProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.config import Config

import direction
import level_cell

class PlayArea(Widget):
    player = ObjectProperty(None)
    level = ObjectProperty(None)

    def generate_level(self):
        self.level.generate_level()
        self.player.size = self.level.cells[0][0].interior
        self.player.center = self.level.cells[0][0].center

    def update(self):
        self.player.move()

        if (self.player.y <= 0 or self.player.top >= self.top):
            self.player.can_move = False
        if (self.player.x <= self.x or self.player.right >= self.right):
            self.player.can_move = False


class Level(Widget):
    """Generate a maze level using the Growing Tree Algorithm
    http://weblog.jamisbuck.org/2011/1/27/maze-generation-growing-tree-algorithm
    """
    padding = NumericProperty()

    columns = NumericProperty(10)
    rows = NumericProperty(10)

    # List to contain generated cells to add as widgets
    cells = ListProperty()
    cell_size = ObjectProperty()

    def generate_level(self):
        # List of active cells used in generation algorithm
        active_cells = []
        first_cell_coordinates = self.get_random_coordinates()
        # Pick the first cell to begin generation from randomly
        active_cells.append(self.create_cell(first_cell_coordinates))
        while len(active_cells) > 0:
            self.generate_cells(active_cells)
        self.add_cells()

    def generate_cells(self, active_cells):
        # Determines which index the algorithm generates from.
        # Changing this yields different results
        current_index = len(active_cells) - 1
        current_cell = active_cells[current_index]

        if current_cell.is_initialised():
            # Remove fully initialised cells from the list
            del active_cells[current_index]
            return

        direction = current_cell.get_random_uninitialised_direction()
        next_cell_coords = Vector(*current_cell.coordinates) + Vector(*direction.value)

        if self.contains_coordinates(next_cell_coords):
            next_cell = self.get_cell(next_cell_coords)
            # Create a new cell and set the edges to passage if no cell exists at next_cell_coords
            if next_cell == None:
                next_cell = self.create_cell(next_cell_coords)
                current_cell.get_edge(direction).type = level_cell.CellEdgeType.passage
                next_cell.get_edge(direction.get_opposite()).type = level_cell.CellEdgeType.passage
                active_cells.append(next_cell)
            # If a cell exists at next_cell_coords, set the edges to walls
            else:
                current_cell.get_edge(direction).type = level_cell.CellEdgeType.wall
                next_cell.get_edge(direction.get_opposite()).type = level_cell.CellEdgeType.wall
        # If next_cell_coords is outside the level, set the edge to a wall
        else:
            current_cell.get_edge(direction).type = level_cell.CellEdgeType.wall

    def create_cell(self, (x, y)):
        """Create a Cell at provided grid coordinates"""
        cell = level_cell.Cell()
        cell.size = self.cell_size
        cell.pos = self.get_cell_position((x, y), cell.size)
        cell.coordinates = x, y
        self.cells[x][y] = cell
        return cell

    def add_cells(self):
        for column in self.cells:
             for cell in column:
                 if isinstance(cell, level_cell.Cell):
                     cell.set_edges()
                     # Add widget at index 1 so that PlayerBeetle remains at 0
                     self.add_widget(cell, 1)

    def get_cell_position(self, (x, y), (width, height)):
        """Convert grid coordinates to window coordinates and return as a tuple

        Arguments:
        (x, y) -- grid coordinate tuple
        (width, height) -- window size tuple
        """
        return ((width * x + self.padding, height * y))

    def get_random_direction(self):
        """Return a random direction.Direction"""
        return random.choice(list(direction.Direction))

    def get_random_coordinates(self):
        """Return a random grid coordinate tuple"""
        return (random.randrange(0, self.columns), random.randrange(0, self.rows))

    def get_cell(self, (x, y)):
        """Return the cell at given grid coordinates

        Arguments:
        (x, y) -- grid coordinate tuple
        """
        return self.cells[x][y]

    def contains_coordinates(self, (x, y)):
        """Return True if the grid coordinates are in the allocated level space

        Arguments:
        (x, y) -- grid coordinate tuple"""
        if 0 <= x < self.columns and 0 <= y < self.rows:
            return True


class PlayerBeetle(Widget):
    # set starting position to 0, 0
    x_position = NumericProperty(0)
    y_position = NumericProperty(0)
    position = ReferenceListProperty(x_position, y_position)

    speed = NumericProperty(5)
    color = ObjectProperty((1, 0, 1))

    move_direction = ObjectProperty(direction.Direction.right)

    can_move = BooleanProperty(False)

    def check_destination(self):
        current_cell = self.parent.level.cells[self.x_position][self.y_position]
        if current_cell.get_edge(self.move_direction).type == level_cell.CellEdgeType.wall:
            self.can_move = False

    def move(self):
        self.check_destination()
        self.update_position()
        if self.can_move:
            self.pos = Vector(self.move_direction.value[0] * self.speed,
                              self.move_direction.value[1] * self.speed) + self.pos

    def update_position(self):
        """Updates the stored position of the player in grid coordinates"""
        target_position_x = self.position[0] + self.move_direction.value[0]
        target_position_y = self.position[1] + self.move_direction.value[1]
        target_cell = self.parent.level.cells[target_position_x][target_position_y]
        if (self.collide_widget(target_cell) and
                not self.collide_widget(self.parent.level.cells[self.x_position][self.y_position])):
            self.position = target_position_x, target_position_y


class HotrodGame(Widget):
    play_area = ObjectProperty(None)
    # Allow game controller access to player widget
    player = ObjectProperty(None)

    def start(self):
        self.play_area.generate_level()

    def update(self, dt):
        self.play_area.update()

    def on_touch_up(self, touch):
        # Move right if player swipes right
        if touch.pos[0] > touch.opos[0] + self.width/10:
            self.player.can_move = True
            self.player.move_direction = direction.Direction.right
        # Move left if player swipes left
        if touch.pos[0] < touch.opos[0] - self.width/10:
            self.player.can_move = True
            self.player.move_direction = direction.Direction.left
        # Move up is player swipes up
        if touch.pos[1] > touch.opos[1] + self.height/10:
            self.player.can_move = True
            self.player.move_direction = direction.Direction.up
        # Move down if player swipes down
        if touch.pos[1] < touch.opos[1] - self.height/10:
            self.player.can_move = True
            self.player.move_direction = direction.Direction.down
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