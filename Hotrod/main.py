__author__ = 'Harriet'

import random
from enum import Enum

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty, ReferenceListProperty, ListProperty, BooleanProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.config import Config

import direction

class PlayArea(Widget):
    player = ObjectProperty(None)

    columns = NumericProperty(10)
    rows = NumericProperty(10)

    cells = ListProperty()
    cell_size = ObjectProperty()

    padding = NumericProperty()

    # def generate_level(self):
    #     self.cells = [[None for i in range(self.columns)] for i in range(self.rows)]
    #     for x in range(self.columns):
    #         for y in range(self.rows):
    #             coordinates = x, y
    #             self.create_cell(coordinates)
    #     for column in self.cells:
    #         for cell in column:
    #             cell.set_edges()
    #             # Add widget at index 1 so that PlayerBeetle remains at 0
    #             self.add_widget(cell, 1)
    #
    #     self.player.size = self.cells[0][0].interior
    #     self.player.center = self.cells[0][0].center

    def generate_level(self):
        active_cells = []
        self.set_first_cell(active_cells)
        while len(active_cells) > 0:
            self.generate_cells(active_cells)
        self.add_cells_to_playarea()
        print self.cells
        self.player.size = self.cells[0][0].interior
        self.player.center = self.cells[0][0].center

    def add_cells_to_playarea(self):
        for column in self.cells:
             for cell in column:
                 # Add widget at index 1 so that PlayerBeetle remains at 0
                 if isinstance(cell, Cell):
                     cell.set_edges()
                     self.add_widget(cell, 1)

    def set_first_cell(self, active_cells):
        active_cells.append(self.create_cell(self.get_random_coordinates()))

    def generate_cells(self, active_cells):
        current_index = len(active_cells) - 1
        current_cell = active_cells[current_index]

        if current_cell.is_initialised():
            del active_cells[current_index]
            return

        direction = current_cell.get_random_uninitialised_direction()
        coordinates = Vector(*current_cell.coordinates) + Vector(*direction.value)

        if self.contains_coordinates(coordinates):
            next_cell = self.get_cell(coordinates)
            if next_cell == None:
                next_cell = self.create_cell(coordinates)
                current_cell.get_edge(direction).type = CellEdgeType.passage
                next_cell.get_edge(direction.get_opposite()).type = CellEdgeType.passage
                active_cells.append(next_cell)
            else:
                current_cell.get_edge(direction).type = CellEdgeType.wall
                next_cell.get_edge(direction.get_opposite()).type = CellEdgeType.wall
        else:
            current_cell.get_edge(direction).type = CellEdgeType.wall


    def create_cell(self, (x, y)):
        """Create a Cell at provided grid coordinates"""
        cell = Cell()
        cell.size = self.cell_size
        cell.pos = self.get_cell_position((x, y), cell.size)
        cell.coordinates = x, y
        self.cells[x][y] = cell
        return cell

    def get_cell_position(self, (x, y), (width, height)):
        """Convert grid coordinates to window coordinates"""
        return ((width * x + self.padding, height * y))

    def update(self):
        self.player.move()

        if (self.player.y <= 0 or self.player.top >= self.top):
            self.player.can_move = False
        if (self.player.x <= self.x or self.player.right >= self.right):
            self.player.can_move = False

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

    def get_random_direction(self):
        return random.choice(list(direction.Direction))

    def get_random_coordinates(self):
        return (random.randrange(0, self.columns), random.randrange(0, self.rows))

    def get_cell(self, (x, y)):
        return self.cells[x][y]

    def contains_coordinates(self, (x, y)):
        if 0 <= x < self.columns and 0 <= y < self.rows:
            return True


class Wall(Widget):
    angle = NumericProperty(0)
    origin = ObjectProperty((0,0))

class CellEdgeType(Enum):
    passage = 0
    wall = 1


class CellEdge(Widget):
    type = ObjectProperty(None)
    direction = ObjectProperty(None)

    cell = ObjectProperty()
    bordering_cell = ObjectProperty()


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


class Cell(Widget):
    coordinates_x = NumericProperty(0)
    coordinates_y = NumericProperty(0)
    coordinates = ReferenceListProperty(coordinates_x, coordinates_y)

    sides = NumericProperty(4)
    wall_thickness = NumericProperty(0.1)
    interior = ListProperty()

    left_edge = ObjectProperty(None)
    right_edge = ObjectProperty(None)
    top_edge = ObjectProperty(None)
    bottom_edge = ObjectProperty(None)

    edges = ListProperty()
    initialised_edges = NumericProperty(0)

    def set_edges(self):
        """Set the edges to the appropriate type"""
        for edge in self.edges:
            edge.set_edge()

    def get_edge(self, direction):
        for edge in self.edges:
            if edge.direction == direction:
                return edge


    def is_initialised(self):
        for edge in self.edges:
            if edge.type == None:
                return False
        return True

    def get_random_uninitialised_direction(self):
        edges = self.edges[:]
        for i in range(self.sides):
            random_edge = random.choice(edges)
            if random_edge.type == None:
                return random_edge.direction
            else:
                edges.remove(random_edge)


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
        if self.parent.cells[self.x_position][self.y_position].get_edge(self.move_direction).type == CellEdgeType.wall:
            self.can_move = False

    def move(self):
        self.update_position()
        self.check_destination()
        if self.can_move:
            self.pos = Vector(self.move_direction.value[0] * self.speed,
                              self.move_direction.value[1] * self.speed) + self.pos

    def update_position(self):
        target_position_x = self.position[0] + self.move_direction.value[0]
        target_position_y = self.position[1] + self.move_direction.value[1]
        if (self.collide_widget(self.parent.cells[target_position_x][target_position_y]) and
                not self.collide_widget(self.parent.cells[self.x_position][self.y_position])):
            self.position = target_position_x, target_position_y



class HotrodGame(Widget):
    play_area = ObjectProperty(None)

    def start(self):
        self.play_area.generate_level()

    def update(self, dt):
        self.play_area.update()


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