from __future__ import annotations

from pygame import Clock, Surface, event, display, Vector2
from pygame.sprite import DirtySprite, LayeredDirty
from src.classes.event_emitter import EventEmitter
from src.classes.sprite_object import Sprite
from src.static_config import GRID_SIZE
from src.classes.camera import Camera
from typing import TYPE_CHECKING, Any
from src.classes.input import Input
import pygame


if TYPE_CHECKING:
    from src.classes.game_object import GameObject


class Game(EventEmitter):
    DEBUG = True

    def __init__(self):
        super().__init__()

        self.surface = display.set_mode((1280, 720), pygame.RESIZABLE)
        self.surface.fill((0, 0, 0))
        self.sprite_layers: LayeredDirty[DirtySprite] = LayeredDirty(default_layer=1)
        self.camera = Camera(self)
        self.input = Input(self)
        self.objects: list[GameObject] = []
        self.bg = Surface((1280, 720))
        self.bg.fill("black")

        if Game.DEBUG:
            self.objects.append(
                Sprite(
                    self,
                    "/Users/hayper/Downloads/pixil-frame-0.png",
                )
            )
            self.objects.append(
                Sprite(
                    self,
                    "/Users/hayper/Downloads/pixil-frame-0.png",
                    position=Vector2(1280 - GRID_SIZE, 0),
                )
            )
            self.objects.append(
                Sprite(
                    self,
                    "/Users/hayper/Downloads/pixil-frame-0.png",
                    position=Vector2(0, 720 - GRID_SIZE),
                )
            )
            self.objects.append(
                Sprite(
                    self,
                    "/Users/hayper/Downloads/pixil-frame-0.png",
                    position=Vector2(1280 - GRID_SIZE, 720 - GRID_SIZE),
                )
            )

        display.set_caption("Funky Factory Game")

        # stuff
        self.__requested_flip = False

    def request_flip(self):
        self.bg = Surface(display.get_window_size())
        self.bg.fill("black")
        self.__requested_flip = True

    def start(self):
        try:
            running = True
            clock = Clock()
            dt = 0

            while running:
                events = event.get()

                for evt in events:
                    if evt.type == pygame.QUIT:
                        running = False
                        break
                    else:
                        self.emit(f"PYGAME_{evt.type}", evt.dict)

                if self.__requested_flip:
                    self.surface.fill("black")
                else:
                    self.sprite_layers.clear(self.surface, self.bg)

                if not running:
                    break

                updateables: list[Any] = [self.camera, self.input]
                updateables.extend(self.objects)

                for x in updateables:
                    x.update(dt)

                for x in self.objects:
                    if not x.visible:
                        continue
                    x.render(self.surface)

                rects = self.sprite_layers.draw(self.surface)
                if self.__requested_flip:
                    display.flip()
                else:
                    display.update(rects)

                if self.__requested_flip:
                    self.__requested_flip = False

                dt = clock.tick(60) / 1000
        except KeyboardInterrupt:
            pass
