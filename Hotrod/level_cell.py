"""Store classes relating to the level's individual cells.

This module stores classes that store information about and manage the
levels individual cells. Cells and cell edges are accessed through this module.

Classes:
Cell(Widget) -- widget representing level cell
CellEdge(Widget) -- widget for the edges of the cell
Wall(Widget) -- widget representing cell walls
CellEdgeType(Enum) -- enum for classifying an edge as a wall or a passage
"""

# Standard Python library
import random

# Kivy modules
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty, ReferenceListProperty, ListProperty, BooleanProperty
from kivy.vector import Vector

# Other modules
from enum import Enum

# Own modules
import collectable
import direction


class Cell(Widget):

    """Store properties and methods relating to individual cells.

    This class stores Kivy properties relating to individual cells and
    keeps track of the cell's edges.
    It must be instantiated as a child of the level.Level class.

    Widget Children:
    Four CellEdge widgets
    collectable.Pellet widget

    Public Methods:
    get_edge -- return the edge in a given direction
    is_initialised -- return True if cell is fully initialised
    get_random_uninitialised_direction -- return a random uninitialised direction
    get_walls -- return a list of edges that are walls
    update_cell -- update the cell's size and position
    initialise_pellets -- set the cell's pellet's type
    remove_pellet -- remove the cell's pellet

    Kivy Properties:
    coordinates_x -- NumericProperty to store the cell's x grid coordinates
    coordinates_y -- NumericProperty to store the cell's y grid coordinates
    coordinates -- ReferenceListProperty to store the cell's grid coordinates
    pellet_exists -- BooleanProperty to determine whether the cell contains a pellet
    interior -- the dimensions of the interior of the cell (kv file)
    edges -- ListProperty storing references to the cell's edges (kv file)
    sides -- NumericProperty storing the number of sides the cell has (kv file)
    wall_thickness -- NumericProperty storing the size of the cell's walls relative to the cell (kv file)
    """

    coordinates_x = NumericProperty(0)
    coordinates_y = NumericProperty(0)
    coordinates = ReferenceListProperty(coordinates_x, coordinates_y)

    pellet_exists = BooleanProperty()

    def get_edge(self, direction):
        """Return the CellEdge widget corresponding to the given direction.

        This method returns a reference to one of its edges in the specified
        direction. This should be used for access to specific cell edges by this
        and other classes.

        Arguments:
        direction -- the direction of the side of the cell the edge is on as a direction.Direction
        """

        for edge in self.edges:
            if edge.direction == direction:
                return edge

    def all_edges_initialised(self):
        """Check if all cell edges have been initialised.

        This method returns True if all cell edges have
        been assigned a type.
        """

        for edge in self.edges:
            if edge.type == None:
                return False
        return True

    def get_random_uninitialised_direction(self):
        """Return a random direction with an uninitialised edge.

        This method returns a random direction.Direction where the edge has
        not yet been assigned a type.
        """

        edges = self.edges[:]
        for i in range(self.sides):
            random_edge = random.choice(edges)
            if random_edge.type == None:
                return random_edge.direction
            else:
                edges.remove(random_edge)

    def get_walls(self):
        """Return a list of the cell's edges that are walls."""

        walls = []
        for edge in self.edges:
            if edge.type == CellEdgeType.wall:
                walls.append(edge)
        return walls

    def update_cell_size(self):
        """Update the cell and its children's size and position.

        This method ensures that cells are the correct size and that their
        children's sizes and positions are set accordingly. It should be
        called whenever the window size changes.
        """

        self.size = self.parent.cell_size
        self.pos = self.parent.convert_to_window_position(self.coordinates)

        for edge in self.edges:
            edge.height = self.height + (2 * self.height * self.wall_thickness)
            edge.width = self.width * self.wall_thickness
            edge.pos = (self.pos[0], self.pos[1] - self.height * self.wall_thickness)
            edge.update_edge_widget()

        if self.pellet_exists:
            self.pellet.update_pellet_widget()

    def initialise_pellets(self):
        """Set whether a pellet exists and set its type to normal.

        This method sets up the pellet contained in the cell.
        If the cell is in the beetle den or player start position,
        the cell's pellet is removed. Otherwise, the pellet type
        is assigned to normal and the game's pellet count is increased.
        """

        self.parent.game.pellet_count += 1

        if self in self.parent.beetle_den.itervalues() or self.coordinates == self.parent.game.player.start_position:
            self.remove_pellet()
        else:
            self.pellet.type = collectable.PelletType.normal
            self.pellet_exists = True

    def remove_pellet(self):
        """Remove the pellet from the cell.

        This method removes the pellet from the cell and sets the
        cell's pellet existence to false. It also decreases the games
        current pellet count.
        """

        self.remove_widget(self.pellet)
        self.pellet_exists = False
        self.parent.game.pellet_count -= 1

    def add_power_pellet(self):
        """Set the type of pellet in the cell to power pellet.

        This method sets the type of pellet the cell contains to a power pellet.
        It also binds the pellet's existence to the enemies' frightened state, so
        that remaining enemies still become frightened if the player collects an
        additional power up whilst powered up.
        The pellet existence is also bound to the players' powerup activation method.
        """

        self.pellet.type = collectable.PelletType.power
        for enemy in self.parent.game.enemies:
            self.bind(pellet_exists=enemy.switch_frightened_state)
            self.bind(pellet_exists=self.parent.game.player.activate_powerup)


class CellEdge(Widget):

    """Store methods and properties relating to cell edges.

    This class manages the size and position of the cell's edges and
    stores information relating to its type and direction.

    Kivy Events:
    on_type -- updates the child widget when the edge's type changes

    Public Methods:
    update_edge_widget -- ensures that the edge is displaying the correct widget
    """

    type = ObjectProperty(None)

    def update_edge_widget(self):
        """Ensure that the edge has the correct child widget.

        This method ensures that the edge possesses a wall widget
        if the edge is a wall. It also ensures that the wall widget
        is the correct size and position.
        It should be called when the edge type or window size changes.
        """

        self.clear_widgets()
        if self.type == CellEdgeType.wall:
            wall = Wall()
            wall.size = self.size
            wall.pos = self.pos
            wall.rotation_origin = self.parent.center
            wall.rotation = self.direction.get_angle()
            self.add_widget(wall)

    def on_type(self, instance, value):
        """Update edge's child widgets when edge type changes.

        This Kivy event is called when the self.type changes and triggers
        the edge's child widgets to be updated.
        """

        self.update_edge_widget()


class Wall(Widget):
    """Store information relating to wall widgets.

    This class is defined in the kv file.
    """

    pass


class CellEdgeType(Enum):
    """Store enumerations for cell edge types.

    This is an enum to represent the types an edge can have.
    """

    # Arbitrary numbers for enum
    passage = 0
    wall = 1

