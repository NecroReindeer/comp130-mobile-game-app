"""Contain a class for managing level generation.

This module contains a class that manages level generation and
allows access to the level's cells.

Classes:
Level(Widget) -- class for generating level and storing information about the level
"""

# Standard python library
import random

# Kivy modules
from kivy.uix.widget import Widget
from kivy.vector import Vector
from kivy.properties import ObjectProperty, NumericProperty, ListProperty

# Own modules
import direction
import collectable
import level_cell
import error


# Minimum number of cells from the edge the beetle den must be
# Should always be greater than 1 and less than columns/2 - beetle den size
BEETLE_DEN_PADDING_X = 1
# Should always be greater than 1 and less than rows/2
BEETLE_DEN_PADDING_Y = 1


class Level(Widget):

    """Store methods required for level generation and management.

    This class stores methods and properties relating to level generation and
    level management. An array of cells is stored in this class to provide acces
    to cells.

    Public methods:
    generate_level() -- start level generation process
    get_cell((x, y)) -- return the cell at the given grid coordinates
    get_adjacent_cell(cell, direction) -- return the adjacent cell in a given direction
    convert_to_grid_position((x, y)) -- convert window coordinates to grid coordinates
    convert_to_window_position((x, y)) -- convert grid coordinates to window coordinates

    Children:
    level_cell.Cell instances (after level generation)
    """

    # List to contain generated cells to add as widgets
    cells = ListProperty()

    # Dictionary to contain cells in the beetle den
    beetle_den = ObjectProperty()

    def generate_level(self):
        """Generate and set up a level.

        This method manages the level generation process, ensuring that the
        level is generated and all play elements are added.
        """

        # Ensure generation starts from an empty level
        self.__clear_level()
        self.__generate_maze()
        self.__remove_dead_ends()
        self.__create_den()
        self.__add_cells()
        self.__add_powerups()

    def get_cell(self, (x, y)):
        """Return the cell at given grid coordinates.

        This method returns a reference to the cell at the given grid coordinates.
        This should be used for accessing cells from this or other classes.

        Arguments:
        (x, y) -- grid coordinates as a tuple
        """

        return self.cells[x][y]

    def get_adjacent_cell(self, cell, direction):
        """Return the adjacent Cell in a given direction.

        This method returns a reference to an adjacent cell in a given direction
        relative to the given cell. If one doesn't exist, None is returned.
        It should be used for easily accessing neighboring cells.

        Arguments:
        cell - the cell that the adjacent cell is relative to as a level_cell.Cell
        direction - the direction that you want to get the adjacent cell as direction.Direction
        """

        adjacent_cell_coords = Vector(*cell.coordinates) + direction.value
        if self.__contains_coordinates(adjacent_cell_coords):
            adjacent_cell = self.get_cell(adjacent_cell_coords)
            return adjacent_cell
        else:
            return None

    def convert_to_grid_position(self, (x, y)):
        """Return grid coordinates converted from window coordinates.

        This method converts window position coordinates to the game's level grid coordinates.
        It returns the grid coordinates as a tuple.

        Arguments:
        (x, y) -- window position coordinates as a tuple
        """

        grid_x = int((x - self.x) / self.cell_size[0])
        grid_y = int(y / self.cell_size[1])
        return grid_x, grid_y

    def convert_to_window_position(self, (x, y)):
        """Return window coordinates converted from grid coordinates.

        This method converts grid position coordinates to the window position coordinates.
        It returns the window position coordinates as a tuple.

        Arguments:
        (x, y) -- grid position coordinates tuple
        """

        window_x = self.cell_size[0] * x + self.x
        window_y = self.cell_size[1] * y
        return window_x, window_y

    def __clear_level(self):
        """Remove all widgets from the level and reset the cell list"""

        self.clear_widgets()
        self.cells = [[None for i in range(self.rows)] for i in range(self.columns)]

    def __generate_maze(self):
        """Procedurally generate a maze.

        This method begins the process of procedurally generating a maze using the Growing Tree Algorithm
        (described here http://weblog.jamisbuck.org/2011/1/27/maze-generation-growing-tree-algorithm)
        The cell to start generation from is chosen randomly, before beginning the full maze generation process.
        """

        # List of active cells used in generation algorithm
        active_cells = []
        # Pick the first cell to begin generation from randomly
        first_cell_coordinates = self.__get_random_coordinates()
        active_cells.append(self.__create_cell(first_cell_coordinates))

        while len(active_cells) > 0:
            self.__generate_cells(active_cells)

    def __generate_cells(self, active_cells):
        """Generate the cells for the maze.

        This method generates the cells for the maze using the Growing Tree Algorithm,
        storing the information about them in self.cells. Widgets are not added at this stage.

        Arguments:
        active_cells -- list of active cells. It should contain the starting cell as a level_cell.Cell.
        """

        # Determines which index the algorithm generates from. Changing this yields different results.
        current_index = len(active_cells) - 1         # Last index
        current_cell = active_cells[current_index]

        if current_cell.all_edges_initialised():
            # Remove fully initialised cells from the list so that they are not revisited
            del active_cells[current_index]
            return

        direction = current_cell.get_random_uninitialised_direction()
        # Not using self.get_adjacent_cell as only coordinates are needed here
        next_cell_coords = Vector(*current_cell.coordinates) + direction.value

        if self.__contains_coordinates(next_cell_coords):
            next_cell = self.get_cell(next_cell_coords)
            if next_cell == None:
                # Create a new cell and set the relevant edges to passages if no cell exists at next_cell_coords
                next_cell = self.__create_cell(next_cell_coords)
                current_cell.get_edge(direction).type = level_cell.CellEdgeType.passage
                # Set corresponding edge of the other cell to a passage too, otherwise it will later become a wall
                next_cell.get_edge(direction.get_opposite()).type = level_cell.CellEdgeType.passage
                active_cells.append(next_cell)

            else:
                # If a cell exists at next_cell_coords, set the relevant edges to walls
                current_cell.get_edge(direction).type = level_cell.CellEdgeType.wall
                next_cell.get_edge(direction.get_opposite()).type = level_cell.CellEdgeType.wall

        # If next_cell_coords is outside the level boundaries, set the edge to a wall
        else:
            current_cell.get_edge(direction).type = level_cell.CellEdgeType.wall

    def __remove_dead_ends(self):
        """Ensure that there are no single-cell dead ends.

        This method removes any single-cell dead ends by selecting a
        random wall to remove. This should be done after all other methods
        that affect the maze layout have been executed.
        Dead ends are removed to prevent the game from being impossibly hard,
        and to accommodate enemies being forbidden to reverse direction.
        """

        for column in self.cells:
            for cell in column:
                walls = cell.get_walls()
                # A cell is a dead end if all sides are walls except for one
                if len(walls) >= cell.sides - 1:
                    # Choose a random wall to be removed and attempt to remove it
                    target_edge = random.choice(walls)
                    while True:
                        try:
                            self.__set_edge_to_passage(cell, target_edge.direction)
                            break
                        except error.NonExistentCellError:
                            # If the wall is at the edge, remove it from the list of walls
                            walls.remove(target_edge)
                            target_edge = random.choice(walls)

    def __set_edge_to_passage(self, cell, direction):
        """Change a given edge of a cell to a passage.

        This method sets a cell edge type of a given cell in a given direction
        to a passage, and also sets the corresponding edge in the adjacent cell to a passage.
        Note that edges at the edge of the level cannot be changed into passages.

        Arguments:
        cell - the level_cell.Cell whose edge will be changed
        direction - the direction of the edge to be changed as a direction.Direction
        """
        edge = cell.get_edge(direction)
        adjacent_cell = self.get_adjacent_cell(cell, direction)

        if adjacent_cell != None:
            opposite_edge = adjacent_cell.get_edge(direction.get_opposite())
            opposite_edge.type = level_cell.CellEdgeType.passage
            edge.type = level_cell.CellEdgeType.passage
        else:
            # Cell can only be set to passage if there is an adjacent cell
            raise error.NonExistentCellError("There is no adjacent cell.")

    def __set_edge_to_wall(self, cell, direction):
        """Change a given edge of a cell to a passage.

        This method sets a cell edge type of a given cell in a given direction
        to a wall, and also sets the corresponding edge in the adjacent cell to a wall.

        Arguments:
        cell - the level_cell.Cell whose edge will be changed
        direction - the direction of the edge to be changed as a direction.Direction
        """
        edge = cell.get_edge(direction)
        edge.type = level_cell.CellEdgeType.wall
        adjacent_cell = self.get_adjacent_cell(cell, direction)

        # Also set relevant edge of adjacent cell if it exists
        if adjacent_cell != None:
            opposite_edge = adjacent_cell.get_edge(direction.get_opposite())
            opposite_edge.type = level_cell.CellEdgeType.wall

    def __set_cell_edges(self, cell, directions):
        """Set all edges of a cell as desired.

        This method sets the edges of the given cell in the given directions to walls.
        All remaining edges are set to passages.

        Arguments:
        cell - the level_cell.Cell whose edges will be changed
        directions - tuple of direction.Direction specifying where walls should be
        """
        for edge in cell.edges:
            if edge.direction in directions:
                self.__set_edge_to_wall(cell, edge.direction)
            else:
                self.__set_edge_to_passage(cell, edge.direction)

    def __create_den(self):
        """Create a den area that enemies will come from.

        This method creats a den area that will serve as the base for
        enemy beetles. The den placement is random, and based on the
        position of its center cell.
        """
        self.beetle_den = {}

        center_coords = self.__get_den_center()

        center_cell = self.get_cell(center_coords)
        left_cell = self.get_adjacent_cell(center_cell, direction.Direction.left)
        right_cell = self.get_adjacent_cell(center_cell, direction.Direction.right)

        self.beetle_den['center'] = center_cell
        self.beetle_den['left'] = left_cell
        self.beetle_den['right'] = right_cell

        self.__initialise_den_edges()
        self.__remove_walls_around_den()

    def __get_den_center(self):
        """Choose random grid coordinates for the center of the den area."""
        # +/- 1 on each x coord to account for cell on either side of center
        den_center_coords = (random.randrange(BEETLE_DEN_PADDING_X + 1, self.columns - BEETLE_DEN_PADDING_X - 1),
                             random.randrange(BEETLE_DEN_PADDING_Y, self.rows - BEETLE_DEN_PADDING_Y))
        return den_center_coords

    def __initialise_den_edges(self):
        """Set the edges of the beetle den correctly.

        This method ensures that the edges of the beetle den are set up correctly.
        The beetle den is enclosed with a one-way exit at the top of the center cell.
        """

        den_center = self.beetle_den['center']

        self.__set_cell_edges(den_center, (direction.Direction.down, direction.Direction.up))
        self.__set_cell_edges(self.beetle_den['left'], (direction.Direction.up, direction.Direction.down, direction.Direction.left))
        self.__set_cell_edges(self.beetle_den['right'], (direction.Direction.up, direction.Direction.down, direction.Direction.right))

        # Manually set top edge of den_center in order to create one-way passage
        den_center.get_edge(direction.Direction.up).type = level_cell.CellEdgeType.passage

    def __remove_walls_around_den(self):
        """Ensure that there is a clear passage around the den.

        This method ensures that there is a clear passage around the circumference
        of the enemy den. This is both to guarantee there are no dead ends around it,
        and reduce difficulty by allowing the player to move freely when near the enemy den.
        """

        for cell in self.beetle_den.itervalues():
            for dir in direction.Direction:
                adjacent_cell = self.get_adjacent_cell(cell, dir)

                if adjacent_cell not in self.beetle_den.itervalues():
                    if dir == direction.Direction.up or dir == direction.Direction.down:
                        for edge_dir in direction.Direction.left, direction.Direction.right:
                            try:
                                self.__set_edge_to_passage(adjacent_cell, edge_dir)
                            except error.NonExistentCellError:
                                pass

                    if dir == direction.Direction.left or dir == direction.Direction.right:
                        for edge_dir in direction.Direction.down, direction.Direction.up:
                            try:
                                self.__set_edge_to_passage(adjacent_cell, edge_dir)
                            except error.NonExistentCellError:
                                pass

    def __create_cell(self, (x, y)):
        """Create a Cell at provided grid coordinates.

        This method adds a level_cell.Cell widget to the array of cells
        and sets up its properties and bindings.
        Note that the widget is not added to the level widget at this stage.

        Arguments:
        (x, y) -- grid coordinates as a tuple
        """
        cell = level_cell.Cell()
        # Bind here so that cells are created before event can be triggered
        self.bind(size=self.game.play_area.update_play_area_size, pos=self.game.play_area.update_play_area_size)
        cell.size = self.cell_size
        cell.pos = self.convert_to_window_position((x, y))
        cell.coordinates = x, y
        self.cells[x][y] = cell
        return cell

    def __add_cells(self):
        """Perform final steps in cell-setup and add them as widgets.

        This method performs the final steps of cell creation, namely
        ensuring they have pellets and adding them as child widgets.
        """

        for column in self.cells:
             for cell in column:
                 self.add_widget(cell)
                 cell.initialise_pellets()

    def __add_powerups(self):
        """Add powerups to random cells.

        This method chooses cells to add powerups to randomly
        until the maximum powerup count has been reached.
        """

        powerup_count = 0
        while powerup_count < self.game.powerup_limit:
            coordinates = self.__get_random_coordinates()
            cell = self.get_cell(coordinates)
            if cell.pellet_exists and cell.pellet.type is not collectable.PelletType.power:
                cell.add_power_pellet()
                powerup_count += 1

    def __get_random_direction(self):
        """Return a random direction.Direction"""

        return random.choice(list(direction.Direction))

    def __get_random_coordinates(self):
        """Return a random grid coordinate tuple"""

        return (random.randrange(self.columns), random.randrange(self.rows))

    def __contains_coordinates(self, (x, y)):
        """Check if the level grid contains the given coordinates.

        This method checks if the level grid contains the supplied coordinates
        and returns True if it does.

        Arguments:
        (x, y) -- grid coordinates as a tuple
        """

        if 0 <= x < self.columns and 0 <= y < self.rows:
            return True

