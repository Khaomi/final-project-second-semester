from __future__ import annotations

from src.classes.event_emitter import EventEmitter
from pygame import Vector2, Rect, Surface
from src.static_config import GRID_SIZE
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
    ):
        super().__init__()
        self.game = game

        """
        Absolute position
        """
        self.position = position if position else Vector2(0, 0)
        """
        Grid size for this object
        """
        self.size = size if size else Vector2(1, 1)
        """
        Current rotation
        """
        self._rotation = rotation % 360

        self.active = True
        self.visible = False

        self.game.camera.on("resize", self.__update_visibility)
        self.game.camera.on("move", self.__update_visibility)
        self.__update_visibility()

    def __update_visibility(self):
        self.visible = self.active and self.game.camera.is_in_camera(self.rect)

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
            self.position.x,
            self.position.y,
            self.size.x * GRID_SIZE,
            self.size.y * GRID_SIZE,
        )

    @property
    def screen_rect(self):
        screen_vec = self.game.camera.world_to_screen(self.position)
        abs_size = self.absolute_size

        return Rect(screen_vec.x, screen_vec.y, abs_size.x, abs_size.y)

    def update(self, dt: float):
        pass

    def render(self, surface: Surface):
        """
        SHOULD ONLY USE THIS WHEN IT IS *REALLY* NEEDED, WE HAVE `Sprite` CLASS THAT DOES DIRTY RENDERING
        """
        pass
