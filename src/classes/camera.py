from __future__ import annotations

from src.classes.event_emitter import EventEmitter
from pygame import Vector2, Rect, display
from typing import TYPE_CHECKING, Any
import pygame


if TYPE_CHECKING:
    from pygame.typing import RectLike
    from src.game import Game


class Camera(EventEmitter):
    def __init__(self, game: Game, position: Vector2 | None = None):
        super().__init__()

        self.game = game
        self._position = position if position else Vector2(0)
        self._size = Vector2(display.get_window_size())

        self.game.on(f"PYGAME_{pygame.WINDOWRESIZED}", self.__on_window_resized)

    def __on_window_resized(self, value: dict[str, Any]):
        self._size = Vector2(value["x"], value["y"])
        self.game.request_flip()
        self.emit("resize")

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value: Vector2):
        self._position = value
        self.emit("move")

    @property
    def rect(self):
        return Rect(
            self.position.x,
            self.position.y,
            self._size.x,
            self._size.y,
        )

    def world_to_screen(self, pos: Vector2):
        return pos - self.position

    def screen_to_world(self, pos: Vector2):
        return pos + self.position

    def is_in_camera(self, rect: RectLike):
        return self.rect.colliderect(rect)

    def update(self, dt: float):
        pass
