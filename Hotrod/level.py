__author__ = 'Harriet'

import random

from kivy.uix.widget import Widget
from kivy.vector import Vector
from kivy.properties import ObjectProperty, NumericProperty, ListProperty

import level_cell
import direction
import collectable

class Level(Widget):
    """Widget for the level.

    Public methods:
    generate_level -- start level generation process"""
    padding = NumericProperty()

    columns = NumericProperty(10)
    rows = NumericProperty(10)

    # List to contain generated cells to add as widgets
    cells = ListProperty()
    cell_size = ObjectProperty()

    pellets = ListProperty()


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
        self.__add_pellets()

    def check_pellet_collisions(self):
        for pellet in self.pellets:
            if pellet.collide_widget(self.parent.player):
                self.remove_widget(pellet)
                self.pellets.remove(pellet)
                self.parent.parent.score += 10






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

    def __add_pellets(self):
        for column in self.cells:
            for cell in column:
                pellet = collectable.Pellet()
                pellet.width = cell.width / 10
                pellet.height = cell.height / 10
                pellet.center = cell.center
                pellet.coordinates = cell.coordinates
                self.pellets.append(pellet)
                self.add_widget(pellet)


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
        adjacent_cell = self.__get_adjacent_cell(cell, edge_direction)
        if adjacent_cell != None:
                        opposite_edge = adjacent_cell.get_edge(edge_direction.get_opposite())
                        opposite_edge.type = level_cell.CellEdgeType.passage
                        edge.type = level_cell.CellEdgeType.passage

    def __get_adjacent_cell(self, cell, direction):
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

