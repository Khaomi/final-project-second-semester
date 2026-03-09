from __future__ import annotations

from src.classes.event_emitter import EventEmitter
from typing import TYPE_CHECKING, Any
from src.objects.item import Item
from pygame import Vector2
import pygame

from src.objects.belt import Belt


if TYPE_CHECKING:
    from src.game import Game


class Input(EventEmitter):
    def __init__(self, game: Game):
        super().__init__()

        self.game = game
        self.__cam_start_position = None
        self.__mouse_start_position = None
        self.__mouse_down = False

        self.__rotation = 0
        self.__tyaf = "belt"

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
        self.game.request_flip(False)

    def __on_mousedown(self, value: dict[str, Any]):
        self.__mouse_down = True
        pos = Vector2(value["pos"][0], value["pos"][1])
        self.__mouse_start_position = pos
        self.__cam_start_position = self.game.camera.position

        world_pos = self.game.camera.screen_to_world(pos)
        obj = Belt(self.game, position=world_pos) if self.__tyaf == "belt" else Item(self.game, position=world_pos)
        obj.rotation = self.__rotation
        obj.snap_to_grid()
        self.game.objects.append(obj)

    def __on_keyup(self, value: dict[str, Any]):
        pass

    def __on_keydown(self, value: dict[str, Any]):
        print(value)
        if value["key"] == 114:
            self.__rotation -= 90
            self.__rotation %= 360
            print(self.__rotation)
        elif value["key"] == 105:
            self.__tyaf = "item" if self.__tyaf == "belt" else "belt"

    def destroy(self):
        self.game.remove_listener(f"PYGAME_{pygame.MOUSEBUTTONUP}", self.__on_mouseup)
        self.game.remove_listener(
            f"PYGAME_{pygame.MOUSEBUTTONDOWN}", self.__on_mousedown
        )
        self.game.remove_listener(f"PYGAME_{pygame.MOUSEMOTION}", self.__on_mousemove)
        self.game.remove_listener(f"PYGAME_{pygame.KEYUP}", self.__on_keyup)
        self.game.remove_listener(f"PYGAME_{pygame.KEYDOWN}", self.__on_keydown)
        self.remove_all_listeners()
