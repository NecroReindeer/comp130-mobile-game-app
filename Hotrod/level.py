"""This module keeps track of things relating to the level, such as cells and pellets.

Classes:
Level(Widget) -- class for generating level and storing information about the level
"""

import random

from kivy.uix.widget import Widget
from kivy.vector import Vector
from kivy.properties import ObjectProperty, NumericProperty, ListProperty

import direction
import collectable
import level_cell
import error

class Level(Widget):
    """Widget for the level.

    Public methods:
    generate_level() -- start level generation process
    check_pellet_collsions() -- check if player has collided with any pellets
    get_cell((x, y)) -- return the cell at the given grid coordinates
    get_adjacent_cell(cell, direction) -- return the adjacent cell in a given direction
    convert_to_grid_position((x, y)) -- convert window coordinates to grid coordinates
    convert_to_window_position((x, y)) -- convert grid coordinates to window coordinates

    Children:
    level_cell.Cell instances (after level generation)
    collectable.Pellet instances (after level generation)
    """
    padding = NumericProperty()

    columns = NumericProperty(10)
    rows = NumericProperty(10)

    # List to contain generated cells to add as widgets
    cells = ListProperty()
    cell_size = ObjectProperty()

    pellets = ListProperty()
    beetle_house = {}

    def generate_level(self):
        """Generate a maze level using the Growing Tree Algorithm
        http://weblog.jamisbuck.org/2011/1/27/maze-generation-growing-tree-algorithm
        """
        # Ensure generation starts from an empty level
        self.__clear_level()
        # List of active cells used in generation algorithm
        active_cells = []
        first_cell_coordinates = self.__get_random_coordinates()
        # Pick the first cell to begin generation from randomly
        active_cells.append(self.__create_cell(first_cell_coordinates))

        while len(active_cells) > 0:
            self.__generate_cells(active_cells)

        self.__remove_dead_ends()
        self.__create_den()
        self.__add_cells()
        self.__add_pellets()

    def check_pellet_collisions(self):
        """Check if player has collided with any pellets. Remove
        the pellet and increase the score if so.
        """
        for pellet in self.pellets:
            if pellet.collide_widget(self.game.player):
                self.remove_widget(pellet)
                self.pellets.remove(pellet)
                self.game.score += 10

    def get_cell(self, (x, y)):
        """Return the cell at given grid coordinates

        Arguments:
        (x, y) -- grid coordinate tuple
        """
        return self.cells[x][y]

    def get_adjacent_cell(self, cell, direction):
        """Return the adjacent Cell in a given direction"""
        adjacent_cell_coords = Vector(*cell.coordinates) + Vector(*direction.value)
        if self.__contains_coordinates(adjacent_cell_coords):
            adjacent_cell = self.get_cell(adjacent_cell_coords)
            return adjacent_cell
        else:
            return None

    def convert_to_grid_position(self, (x, y)):
        """Convert window position coordinates to the game's grid coordinates

        Arguments:
        (x, y) -- window position coordinates tuple
        """
        grid_x = int((x - self.padding) / self.cell_size[0])
        grid_y = int(y / self.cell_size[1])
        return grid_x, grid_y

    def convert_to_window_position(self, (x, y)):
        """Convert grid position coordinates to window coordinates

        Arguments:
        (x, y) -- grid position coordinates tuple
        """
        window_x = self.cell_size[0] * x + self.padding
        window_y = self.cell_size[1] * y
        return window_x, window_y

    def __clear_level(self):
        self.clear_widgets()
        self.cells = [[None for i in range(self.rows)] for i in range(self.columns)]
        self.pellets = []

    def __generate_cells(self, active_cells):
        """Generate the maze

        Arguments:
        active_cells -- list of active cells. Should contain the first cell.
        """
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

        if self.__contains_coordinates(next_cell_coords):
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
        """Add a pellet to each cell in the level
        """
        for column in self.cells:
            for cell in column:
                pellet = collectable.Pellet()
                pellet.width = cell.width / 10
                pellet.height = cell.height / 10
                pellet.center = cell.center
                # To keep track of coordinates for combos
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
                    while True:
                        # If the wall isn't at the edge, remove it
                        try:
                            self.__set_edge_to_passage(cell, target_edge)
                            break
                        except error.NonExistentCellError:
                            walls.remove(target_edge)
                            target_edge = random.choice(walls)

    def __set_edge_to_passage(self, cell, edge):
        """Change a cell edge type to a passage. Also set corresponding
        edge in adjacent cell to a passage"""
        edge_direction = edge.direction
        adjacent_cell = self.get_adjacent_cell(cell, edge_direction)
        if adjacent_cell != None:
            opposite_edge = adjacent_cell.get_edge(edge_direction.get_opposite())
            opposite_edge.type = level_cell.CellEdgeType.passage
            edge.type = level_cell.CellEdgeType.passage
        else:
            raise error.NonExistentCellError("There is no adjacent cell")

    def __set_edge_to_wall(self, cell, edge):
        """Change a cell edge type to a passage. Also set corresponding
        edge in adjacent cell to a passage"""
        edge_direction = edge.direction
        adjacent_cell = self.get_adjacent_cell(cell, edge_direction)
        if adjacent_cell != None:
            opposite_edge = adjacent_cell.get_edge(edge_direction.get_opposite())
            opposite_edge.type = level_cell.CellEdgeType.wall
            edge.type = level_cell.CellEdgeType.wall
        else:
            edge.type = level_cell.CellEdgeType.wall

    def __set_cell_edges(self, cell, directions):
        for edge in cell.edges:
            if edge.direction in directions:
                self.__set_edge_to_wall(cell, edge)
            else:
                self.__set_edge_to_passage(cell, edge)

    def __create_den(self):
        """Create a den area that enemies will come from"""
        center_coords = self.__get_den_center()

        center_cell = self.get_cell(center_coords)
        left_cell = self.get_adjacent_cell(center_cell, direction.Direction.left)
        right_cell = self.get_adjacent_cell(center_cell, direction.Direction.right)

        self.beetle_house['center'] = center_cell
        self.beetle_house['left'] = left_cell
        self.beetle_house['right'] = right_cell

        self.__set_den_edges()
        self.__remove_walls_around_den()

    def __get_den_center(self):
        """Choose a random number for the center of the den area"""
        center_coords = (random.randrange(2, self.columns-1),
                         random.randrange(2, self.rows-1))
        return center_coords

    def __set_den_edges(self):
        self.__set_cell_edges(self.beetle_house['center'], (direction.Direction.down, direction.Direction.up))
        self.__set_cell_edges(self.beetle_house['left'], (direction.Direction.up, direction.Direction.down, direction.Direction.left))
        self.__set_cell_edges(self.beetle_house['right'], (direction.Direction.up, direction.Direction.down, direction.Direction.right))

    def __remove_walls_around_den(self):
        for cell in self.beetle_house.itervalues():
            for dir in direction.Direction:
                adjacent_cell = self.get_adjacent_cell(cell, dir)

                if adjacent_cell not in self.beetle_house.itervalues():
                    if dir == direction.Direction.up or dir == direction.Direction.down:
                        for edge_dir in direction.Direction.left, direction.Direction.right:
                            try:
                                self.__set_edge_to_passage(adjacent_cell, adjacent_cell.get_edge(edge_dir))
                            except error.NonExistentCellError:
                                pass

                    if dir == direction.Direction.left or dir == direction.Direction.right:
                        for edge_dir in direction.Direction.down, direction.Direction.up:
                            try:
                                self.__set_edge_to_passage(adjacent_cell, adjacent_cell.get_edge(edge_dir))
                            except error.NonExistentCellError:
                                pass

    def __create_cell(self, (x, y)):
        """Create a Cell at provided grid coordinates"""
        cell = level_cell.Cell()
        # Bind here so that cells are created before event can be triggered
        self.bind(size=self.game.play_area.update_play_area, pos=self.game.play_area.update_play_area)
        cell.size = self.cell_size
        cell.pos = self.convert_to_window_position((x, y))
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

    def __get_random_direction(self):
        """Return a random direction.Direction"""
        return random.choice(list(direction.Direction))

    def __get_random_coordinates(self):
        """Return a random grid coordinate tuple"""
        return (random.randrange(0, self.columns), random.randrange(0, self.rows))

    def __contains_coordinates(self, (x, y)):
        """Return True if the grid coordinates are in the allocated level space

        Arguments:
        (x, y) -- grid coordinate tuple"""
        if 0 <= x < self.columns and 0 <= y < self.rows:
            return True

