from __future__ import annotations

from src.classes.event_emitter import EventEmitter
from typing import TYPE_CHECKING, Any
from pygame import Vector2
import pygame


if TYPE_CHECKING:
    from src.game import Game


class Input(EventEmitter):
    def __init__(self, game: Game):
        super().__init__()

        self.game = game
        self.__cam_start_position = None
        self.__mouse_start_position = None
        self.__mouse_down = False

        self.game.on(f"PYGAME_{pygame.MOUSEBUTTONUP}", self.__on_mouseup)
        self.game.on(f"PYGAME_{pygame.MOUSEBUTTONDOWN}", self.__on_mousedown)
        self.game.on(f"PYGAME_{pygame.MOUSEMOTION}", self.__on_mousemove)
        self.game.on(f"PYGAME_{pygame.KEYUP}", self.__on_keyup)
        self.game.on(f"PYGAME_{pygame.KEYDOWN}", self.__on_keydown)

    def __on_mouseup(self, _: Any):
        self.__mouse_down = False
        self.__mouse_start_position = None
        self.__cam_start_position = None

    def __on_mousemove(self, value: dict[str, Any]):
        if not self.__mouse_down:
            return

        if self.__cam_start_position is None or self.__mouse_start_position is None:
            return

        pos = Vector2(value["pos"][0], value["pos"][1])
        self.game.camera.position = self.__cam_start_position - (
            pos - self.__mouse_start_position
        )

    def __on_mousedown(self, value: dict[str, Any]):
        self.__mouse_down = True
        pos = Vector2(value["pos"][0], value["pos"][1])
        self.__mouse_start_position = pos
        self.__cam_start_position = self.game.camera.position

    def __on_keyup(self, value: dict[str, Any]):
        pass

    def __on_keydown(self, value: dict[str, Any]):
        pass

    def update(self, dt: float):
        pass
