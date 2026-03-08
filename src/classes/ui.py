from __future__ import annotations

from pygame import SRCALPHA, Rect, Surface, display, draw
from src.classes.event_emitter import EventEmitter
from src.static_config import GRID_SIZE, SPRITE_LAYER
from pygame.sprite import DirtySprite
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.game import Game


class GridSprite(DirtySprite):
    def __init__(self, game: Game):
        super().__init__()

        self.game = game

        self.image: Surface = Surface(
            display.get_window_size(), SRCALPHA
        ).convert_alpha()
        self.rect: Rect = self.image.get_rect(topleft=(0, 0))
        self.dirty = 1
        self.visible = 1

        self.game.camera.on("move", self._redraw)
        self.game.camera.on("resize", self._on_resize)
        self._redraw()

    def _on_resize(self):
        self.image = Surface(display.get_window_size(), SRCALPHA).convert_alpha()
        self.rect = self.image.get_rect(topleft=(0, 0))
        self._redraw()

    def _redraw(self):
        assert self.image is not None
        assert self.rect is not None

        width = self.rect.width
        height = self.rect.height

        self.image.fill((0, 0, 0, 0))

        cam_x = int(self.game.camera.position.x)
        cam_y = int(self.game.camera.position.y)
        x_offset = (-cam_x) % GRID_SIZE
        y_offset = (-cam_y) % GRID_SIZE

        x = x_offset
        while x < width:
            world_x = cam_x + x
            color = (90, 90, 90, 255) if world_x == 0 else (55, 55, 55, 255)
            draw.line(self.image, color, (x, 0), (x, height), 1)
            x += GRID_SIZE

        y = y_offset
        while y < height:
            world_y = cam_y + y
            color = (90, 90, 90, 255) if world_y == 0 else (55, 55, 55, 255)
            draw.line(self.image, color, (0, y), (width, y), 1)
            y += GRID_SIZE

        self.dirty = 1


class UI(EventEmitter):
    def __init__(self, game: Game):
        super().__init__()

        self.game = game
        self.grid_sprite = GridSprite(game)
        self.game.sprite_layers.add(self.grid_sprite, layer=SPRITE_LAYER.GRID)
