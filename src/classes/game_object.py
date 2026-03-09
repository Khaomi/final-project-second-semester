from __future__ import annotations

from src.static_config import GRID_SIZE, ROTATION_DIRECTION_VECTOR, DIRECTION
from src.classes.event_emitter import EventEmitter
from pygame import Vector2, Rect, Surface
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.game import Game


class GameObject(EventEmitter):
    def __init__(
        self,
        game: Game,
        position: Vector2 | None = None,
        size: Vector2 | None = None,
        rotation: int = 0,
        track_camera_visibility: bool = True,
    ):
        super().__init__()
        self.game = game

        self._position = position if position else Vector2(0, 0)
        """
        Absolute position
        """

        self.size = size if size else Vector2(1, 1)
        """
        Grid size for this object
        """
        self._rotation = rotation % 360
        """
        Current rotation
        """

        self.active = True
        self.visible = False

        self.track_camera_visibility = track_camera_visibility
        if track_camera_visibility:
            self.game.camera.on("resize", self.__update_visibility)
            self.game.camera.on("move", self.__update_visibility)

        self.__update_visibility()
        self._update_position_map(self._position)

    ####

    def get_rotation_vector(self, direction: DIRECTION):
        return ROTATION_DIRECTION_VECTOR[self.rotation][direction]

    def get_direction(self, direction: DIRECTION):
        x, y = ROTATION_DIRECTION_VECTOR[self.rotation][direction]
        return self.position + Vector2(x * GRID_SIZE, y * GRID_SIZE)

    def get_forward(self):
        return self.get_direction(DIRECTION.FORWARD)

    def get_left(self):
        return self.get_direction(DIRECTION.LEFT)

    def get_backward(self):
        return self.get_direction(DIRECTION.BACKWARD)

    def get_right(self):
        return self.get_direction(DIRECTION.RIGHT)

    def get_grid_forward(self):
        return self.get_direction(DIRECTION.FORWARD) // GRID_SIZE

    def get_grid_left(self):
        return self.get_direction(DIRECTION.LEFT) // GRID_SIZE

    def get_grid_backward(self):
        return self.get_direction(DIRECTION.BACKWARD) // GRID_SIZE

    def get_grid_right(self):
        return self.get_direction(DIRECTION.RIGHT) // GRID_SIZE

    ####

    def _update_position_map(
        self, new_position: Vector2, old_position: Vector2 | None = None
    ):
        """
        Make sure to call this if your code override default implementation
        """

        new_grid = (int(new_position.x // GRID_SIZE), int(new_position.y // GRID_SIZE))
        old_grid = (
            (int(old_position.x // GRID_SIZE), int(old_position.y // GRID_SIZE))
            if old_position is not None
            else None
        )

        if (
            old_grid
            and old_grid in self.game.position_map
            and (self in self.game.position_map[old_grid])
        ):
            self.game.position_map[old_grid].remove(self)
            if len(self.game.position_map[old_grid]) <= 0:
                del self.game.position_map[old_grid]

        if new_grid not in self.game.position_map:
            self.game.position_map[new_grid] = []

        self.game.position_map[new_grid].append(self)

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value: Vector2):
        self._update_position_map(value, self._position)
        self._position = value

    def __update_visibility(self):
        self.visible = self.active and self.game.camera.is_in_camera(self.rect)

    def snap_to_grid(self):
        # Neat trick :3
        self.grid_position = self.grid_position

    @property
    def grid_position(self):
        return Vector2(
            self.position.x // GRID_SIZE,
            self.position.y // GRID_SIZE,
        )

    @grid_position.setter
    def grid_position(self, value: Vector2):
        self.position = Vector2(
            int(value.x) * GRID_SIZE,
            int(value.y) * GRID_SIZE,
        )

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value: int):
        self._rotation = value % 360

    @property
    def absolute_size(self):
        """
        Absolute size in pixels
        """
        return Vector2(self.size.x * GRID_SIZE, self.size.y * GRID_SIZE)

    @property
    def rect(self):
        return Rect(
            self._position.x,
            self._position.y,
            self.size.x * GRID_SIZE,
            self.size.y * GRID_SIZE,
        )

    @property
    def screen_rect(self):
        screen_vec = self.game.camera.world_to_screen(self._position)
        abs_size = self.absolute_size

        return Rect(screen_vec.x, screen_vec.y, abs_size.x, abs_size.y)

    def update(self, dt: float):
        pass

    def render(self, surface: Surface):
        """
        SHOULD ONLY USE THIS WHEN IT IS *REALLY* NEEDED, WE HAVE `Sprite` CLASS THAT DOES DIRTY RENDERING
        """
        pass

    def destroy(self):
        grid_pos = (int(self.grid_position.x), int(self.grid_position.y))
        if grid_pos in self.game.position_map:
            if self in self.game.position_map[grid_pos]:
                self.game.position_map[grid_pos].remove(self)

            if len(self.game.position_map[grid_pos]) <= 0:
                del self.game.position_map[grid_pos]

        if self in self.game.objects:
            self.game.objects.remove(self)

        if self.track_camera_visibility:
            self.game.camera.remove_listener("resize", self.__update_visibility)
            self.game.camera.remove_listener("move", self.__update_visibility)
        self.remove_all_listeners()
