__author__ = 'Hat'
"""This module includes classes relating to the level's cells.
Classes:
Cell -- widget representing level cell
CellEdge -- widget for the edges of the cell
CellEdgeType -- enum for classifying an edge as a wall or a passage
Wall -- widget representing cell walls"""

import random

from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty, ReferenceListProperty, ListProperty, BooleanProperty
from kivy.vector import Vector

from enum import Enum

import collectable

class Cell(Widget):
    """Widget representing each cell/square on the play area.

    Children -- four CellEdge widgets
    """
    coordinates_x = NumericProperty(0)
    coordinates_y = NumericProperty(0)
    coordinates = ReferenceListProperty(coordinates_x, coordinates_y)

    sides = NumericProperty(4)
    wall_thickness = NumericProperty(0.1)
    # Size of the area in the cell the player can occupy
    interior = ListProperty()

    left_edge = ObjectProperty(None)
    right_edge = ObjectProperty(None)
    top_edge = ObjectProperty(None)
    bottom_edge = ObjectProperty(None)

    edges = ListProperty()
    initialised_edges = NumericProperty(0)

    def set_edges(self):
        """Assign the correct widgets to all of the cell's CellEdge children"""
        for edge in self.edges:
            edge.set_edge()

    def get_edge(self, direction):
        """Return the CellEdge widget corresponding to the given direction

        Arguments:
        direction -- a direction.Direction"""
        for edge in self.edges:
            if edge.direction == direction:
                return edge

    def is_initialised(self):
        """Return True if all CellEdge widgets have been initialised"""
        for edge in self.edges:
            if edge.type == None:
                return False
        return True

    def get_random_uninitialised_direction(self):
        """Return a random uninitialised CellEdge widget"""
        edges = self.edges[:]
        for i in range(self.sides):
            random_edge = random.choice(edges)
            if random_edge.type == None:
                return random_edge.direction
            else:
                edges.remove(random_edge)

    def get_walls(self):
        walls = []
        for edge in self.edges:
            if edge.type == CellEdgeType.wall:
                walls.append(edge)
        return walls


class CellEdge(Widget):
    type = ObjectProperty(None)
    direction = ObjectProperty(None)

    def set_edge(self):
        """Check if the edge should be a wall or a passage and add
        appropriate widget
        """
        if self.type == CellEdgeType.wall:
            wall = Wall()
            wall.size = self.size
            wall.pos = self.pos
            wall.origin = self.parent.center
            wall.angle = self.direction.get_angle()
            self.add_widget(wall)
        elif self.type == CellEdgeType.passage:
            pass


class Wall(Widget):
    angle = NumericProperty(0)
    origin = ObjectProperty((0,0))


class CellEdgeType(Enum):
    passage = 0
    wall = 1

