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
    """Widget for the level"""
    padding = NumericProperty()

    columns = NumericProperty(10)
    rows = NumericProperty(10)

    # List to contain generated cells to add as widgets
    cells = ListProperty()
    cell_size = ObjectProperty()

    def generate_level(self):
        """Generate a maze level using the Growing Tree Algorithm
        http://weblog.jamisbuck.org/2011/1/27/maze-generation-growing-tree-algorithm
        """
        # List of active cells used in generation algorithm
        active_cells = []
        first_cell_coordinates = self.__get_random_coordinates()
        # Pick the first cell to begin generation from randomly
        active_cells.append(self.__create_cell(first_cell_coordinates))
        while len(active_cells) > 0:
            self.__generate_cells(active_cells)
        self.__remove_dead_ends()
        self.__add_cells()

    def __generate_cells(self, active_cells):
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
                next_cell = self.__create_cell(next_cell_coords)
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

    def __remove_dead_ends(self):
        """Ensure that there are no one-cell dead ends"""
        for column in self.cells:
            for cell in column:
                walls = cell.get_walls()
                if len(walls) >= 3:
                    target_edge = random.choice(walls)
                    if cell.coordinates_x == 0 and target_edge.direction == direction.Direction.left:
                        walls.remove(target_edge)
                        target_edge = random.choice(walls)
                    elif cell.coordinates_x == len(self.cells)-1 and target_edge.direction == direction.Direction.right:
                        walls.remove(target_edge)
                        target_edge = random.choice(walls)

                    if cell.coordinates_y == 0 and target_edge.direction == direction.Direction.down:
                        walls.remove(target_edge)
                        target_edge = random.choice(walls)
                    elif cell.coordinates_y == len(self.cells)-1 and target_edge.direction == direction.Direction.up:
                        walls.remove(target_edge)
                        target_edge = random.choice(walls)

                    self.__set_edge_to_passage(cell, target_edge)

    def __set_edge_to_passage(self, cell, edge):
        """Change a cell edge type to a passage. Also set corresponding
        edge in adjacent cell to a passage"""
        edge_direction = edge.direction
        adjacent_cell = self.get_adjacent_cell(cell, edge_direction)
        if adjacent_cell != None:
                        opposite_edge = adjacent_cell.get_edge(edge_direction.get_opposite())
                        opposite_edge.type = level_cell.CellEdgeType.passage
                        edge.type = level_cell.CellEdgeType.passage

    def get_adjacent_cell(self, cell, direction):
        """Return the adjacent Cell in a given direction"""
        adjacent_cell_coords = Vector(*cell.coordinates) + Vector(*direction.value)
        if self.contains_coordinates(adjacent_cell_coords):
            adjacent_cell = self.get_cell(adjacent_cell_coords)
            return adjacent_cell
        else:
            return None

    def __create_cell(self, (x, y)):
        """Create a Cell at provided grid coordinates"""
        cell = level_cell.Cell()
        cell.size = self.cell_size
        cell.pos = self.get_cell_position((x, y), cell.size)
        cell.coordinates = x, y
        self.cells[x][y] = cell
        return cell

    def __add_cells(self):
        """Initialise all cell edges and add all cells as children"""
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
        (width, height) -- cell size tuple
        """
        return ((width * x + self.padding, height * y))

    def __get_random_direction(self):
        """Return a random direction.Direction"""
        return random.choice(list(direction.Direction))

    def __get_random_coordinates(self):
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
    # set starting grid position to 0, 0
    x_position = NumericProperty(0)
    y_position = NumericProperty(0)
    grid_position = ReferenceListProperty(x_position, y_position)

    speed = NumericProperty(5)
    color = ObjectProperty((1, 0, 1))

    current_direction = ObjectProperty(direction.Direction.right)
    next_direction = ObjectProperty(direction.Direction.right)

    def check_position(self):
        """Move the player to the center of the current cell if it
        tries to move through a wall
        """
        current_cell = self.parent.level.cells[self.x_position][self.y_position]
        current_edge = current_cell.get_edge(self.current_direction)
        if current_edge.type == level_cell.CellEdgeType.wall:
            if self.current_direction == direction.Direction.right:
                if self.center_x > current_cell.center_x:
                    self.center_x = current_cell.center_x

            elif self.current_direction == direction.Direction.left:
                if self.center_x < current_cell.center_x:
                    self.center_x = current_cell.center_x

            elif self.current_direction == direction.Direction.up:
                if self.center_y > current_cell.center_y:
                    self.center_y = current_cell.center_y

            elif self.current_direction == direction.Direction.down:
                if self.center_y < current_cell.center_y:
                    self.center_y = current_cell.center_y

    def update_direction(self, (previous_x, previous_y)):
        """Check if there is a pending movement direction and execute it
        if possible
        """
        if self.next_direction != self.current_direction:
            current_cell = self.parent.level.cells[self.x_position][self.y_position]
            current_edge = current_cell.get_edge(self.next_direction)

            if current_edge.type == level_cell.CellEdgeType.passage:
                if self.current_direction == direction.Direction.right:
                    # Set new direction for next frame if player has moved into/past center or is at the center of cell
                    if ((self.center_x >= current_cell.center_x and current_cell.center_x > previous_x)or
                            (self.center_x == current_cell.center_x and previous_x == current_cell.center_x)):
                        self.center_x = current_cell.center_x
                        self.set_direction()

                elif self.current_direction == direction.Direction.left:
                    if ((self.center_x <= current_cell.center_x and current_cell.center_x < previous_x) or
                            (self.center_x == current_cell.center_x and previous_x == current_cell.center_x)):
                        self.center_x = current_cell.center_x
                        self.set_direction()

                elif self.current_direction == direction.Direction.up:
                    if ((self.center_y >= current_cell.center_y and current_cell.center_y > previous_y) or
                            (self.center_y == current_cell.center_y and previous_y == current_cell.center_y)):
                        self.center_y = current_cell.center_y
                        self.set_direction()

                elif self.current_direction == direction.Direction.down:
                    if ((self.center_y <= current_cell.center_y and current_cell.center_y < previous_y) or
                            (self.center_y == current_cell.center_y and previous_y == current_cell.center_y)):
                        self.center_y = current_cell.center_y
                        self.set_direction()

    def set_direction(self):
        self.current_direction = self.next_direction

    def update_position(self):
        """Updates the stored position of the player in grid coordinates"""
        grid_x = int((self.center_x - self.parent.level.padding) / self.parent.level.cell_size[0])
        grid_y = int(self.center_y / self.parent.level.cell_size[1])
        self.grid_position = grid_x, grid_y

    def move(self):
        # Copy of previous window position
        previous_pos = self.center[:]
        self.pos = Vector(self.current_direction.value[0] * self.speed,
                          self.current_direction.value[1] * self.speed) + self.pos
        self.check_position()
        self.update_direction((previous_pos))
        self.update_position()


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