from typing import TYPE_CHECKING, List
import pygame

if TYPE_CHECKING:
    from classes.game import Game


class GameObject:
    def __init__(self, game: "Game", pos=(0, 0)):
        self.game = game
        self.id = f"{self.__class__.__name__}_{id(self)}"
        self._position = (float(pos[0]), float(pos[1]))
        self.direction = 1
        self.cost = 9999999999999999999
        self.force_render = False

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        old_position_grid = self.grid_position
        self._position = value

        position_map = self.game.position_map

        if old_position_grid in position_map:
            if self in position_map[old_position_grid]:
                position_map[old_position_grid].remove(self)
            if len(position_map[old_position_grid]) <= 0:
                del position_map[old_position_grid]

        if self.grid_position not in position_map:
            position_map[self.grid_position] = [self]
        elif self not in position_map[self.grid_position]:
            position_map[self.grid_position].append(self)

    @property
    def grid_position(self):
        return self.world_to_grid(self.position)

    def world_to_grid(self, position):
        size = self.game.SIZE_PER_TILE
        return (
            int(position[0] // size),
            int(position[1] // size),
        )

    def grid_to_world(self, grid_position):
        size = self.game.SIZE_PER_TILE
        return (
            grid_position[0] * size,
            grid_position[1] * size,
        )

    def world_to_camera(self, position):
        return self.game.camera.to_camera_position(position)

    def to_grid(self):
        return self.world_to_grid(self.position)

    def to_camera(self):
        return self.world_to_camera(self.position)

    def set_position(self, position):
        self.position = (float(position[0]), float(position[1]))

    def snap_to_grid(self):
        self.position = self.grid_to_world(self.grid_position)

    def _direction_vector(self):
        if self.direction == 1:
            return (0, 1)
        elif self.direction == 2:
            return (-1, 0)
        elif self.direction == 3:
            return (0, -1)
        elif self.direction == 4:
            return (1, 0)
        return (0, 0)

    def get_forward(self):
        dx, dy = self._direction_vector()
        x, y = self.grid_position
        return (x + dx, y + dy)

    def get_backward(self):
        dx, dy = self._direction_vector()
        x, y = self.grid_position
        return (x - dx, y - dy)

    def get_left(self):
        dx, dy = self._direction_vector()
        x, y = self.grid_position
        return (x - dy, y + dx)

    def get_right(self):
        dx, dy = self._direction_vector()
        x, y = self.grid_position
        return (x + dy, y - dx)

    def update(self, dt: int, events: List[pygame.event.Event]):
        pass

    def move(self, position):
        self.position = position
        self.snap_to_grid()

    def render(self, screen: pygame.Surface):
        if not self.game.DEBUG:
            return

        elements = [
            self.game.FONTS["Arial"].render(
                f"Obj Type: {self.__class__.__name__}", True, "White"
            ),
            self.game.FONTS["Arial"].render(
                f"Position: {self.position}", True, "White"
            ),
            self.game.FONTS["Arial"].render(
                f"Grid Pos: {self.grid_position}", True, "White"
            ),
        ]
        elements.reverse()

        for x in range(len(elements)):
            screen.blit(
                elements[x],
                self.world_to_camera(
                    (
                        self.position[0] - (self.game.SIZE_PER_TILE / 2),
                        (self.position[1] - (self.game.SIZE_PER_TILE) / 2) - ((x) * 18),
                    )
                ),
            )

    def add_to_game(self):
        self.game.add_object(self)

    def remove_from_game(self):
        self.game.remove_object(self)

    @property
    def is_in_game(self):
        return self in self.game.objects

    def to_dict(self):
        return {
            "type": "object",
            "position": self.position,
            "direction": self.direction,
        }

    @staticmethod
    def from_dict(game, data):
        instance = GameObject(game, pos=data.get("position", (0, 0)))
        instance.direction = data.get("direction", 1)
        return instance
