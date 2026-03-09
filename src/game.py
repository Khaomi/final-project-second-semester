from __future__ import annotations

from pygame import Clock, Surface, event, display, Rect
from pygame.sprite import DirtySprite, LayeredDirty
from src.classes.event_emitter import EventEmitter
from src.static_config import GRID_SIZE
from src.objects.sprite import Sprite
from src.classes.camera import Camera
from typing import TYPE_CHECKING, Any
from src.classes.input import Input
from src.objects.belt import Belt
from src.classes.ui import UI
import logging
import pygame


if TYPE_CHECKING:
    from src.classes.game_object import GameObject
    from pygame import FRect


# Got this formatter from the internet
def setup_logger(level: int):
    logger = logging.getLogger("Funky Factory Game")
    logger.setLevel(level)

    handler = logging.StreamHandler()
    handler.setLevel(level)

    COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[35m",
        "RESET": "\033[0m",
    }

    class ColoredFormatter(logging.Formatter):
        def format(self, record: Any):
            color = COLORS.get(record.levelname, COLORS["RESET"])
            record.levelname = f"{color}[{record.levelname}]{COLORS['RESET']}"
            record.name = f"\033[1m{record.name}\033[0m"
            return f"{record.name} {record.levelname} → {record.getMessage()}"

    formatter = ColoredFormatter()
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


class Game(EventEmitter):
    DEBUG = True

    def __init__(self):
        super().__init__()

        self.logger = setup_logger(logging.DEBUG if self.DEBUG else logging.INFO)
        self.logger.debug("Start")

        self.surface = display.set_mode((1280, 720), pygame.RESIZABLE)
        self.surface.fill((0, 0, 0))
        self.sprite_layers: LayeredDirty[DirtySprite] = LayeredDirty(default_layer=1)
        self.camera = Camera(self)
        self.input = Input(self)
        self.ui = UI(self)
        self.objects: list[GameObject] = []
        self.bg = Surface((1280, 720))
        self.bg.fill("black")

        self.position_map: dict[tuple[int, int], list[GameObject]] = {}

        display.set_caption("Funky Factory Game")

        # stuff
        self.__requested_flip = False

    def request_flip(self, rebuild_bg: bool = True):
        if rebuild_bg:
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

                # for x in updateables:
                #     x.update(dt)
                self.emit("update", dt)

                for x in self.objects:
                    if not x.visible:
                        continue
                    if isinstance(x, Sprite):
                        continue
                    x.render(self.surface)

                rects: list[FRect | Rect] = []
                for x in self.sprite_layers.draw(self.surface):
                    if x.width > 0 or x.height > 0:
                        rects.append(x)

                if self.DEBUG:
                    for x in self.objects:
                        debug_rect = x.screen_rect.copy()
                        rects.append(debug_rect.inflate(2, 2))
                        pygame.draw.rect(
                            self.surface,
                            "GREEN" if x.visible else "RED",
                            debug_rect,
                            width=1,
                        )

                    drawn_links: set[tuple[int, int]] = set()
                    for x in self.objects:
                        if not isinstance(x, Belt):
                            continue

                        neighbors: list[Belt] = [x.next] if x.next else []
                        neighbors.extend(x.prevs)

                        for neighbor in neighbors:
                            x_id = id(x)
                            neighbor_id = id(neighbor)
                            link_key = (
                                (x_id, neighbor_id)
                                if x_id <= neighbor_id
                                else (neighbor_id, x_id)
                            )
                            if link_key in drawn_links:
                                continue
                            drawn_links.add(link_key)

                            a = self.camera.world_to_screen(x.position)
                            b = self.camera.world_to_screen(neighbor.position)

                            a_line = (
                                a.x + (GRID_SIZE / 2),
                                a.y + (GRID_SIZE / 2),
                            )
                            b_line = (
                                b.x + (GRID_SIZE / 2),
                                b.y + (GRID_SIZE / 2),
                            )

                            min_x = int(min(a_line[0], b_line[0]))
                            min_y = int(min(a_line[1], b_line[1]))
                            width = max(1, int(abs(b_line[0] - a_line[0])))
                            height = max(1, int(abs(b_line[1] - a_line[1])))
                            rects.append(
                                Rect(min_x, min_y, width, height).inflate(2, 2)
                            )
                            pygame.draw.line(
                                self.surface,
                                "GREEN",
                                a_line,
                                b_line,
                                width=1,
                            )

                # This is here for quick debugging purpose, it's really noisy so i would like if it doesn't do that
                if self.DEBUG and False:
                    if self.__requested_flip:
                        self.logger.debug("FULL REDRAW!")
                    elif len(rects) > 0:
                        self.logger.debug("Got draw request for => %s", rects)
                    else:
                        self.logger.debug("No draw request")
                if self.__requested_flip:
                    display.flip()
                else:
                    display.update(rects)

                if self.__requested_flip:
                    self.__requested_flip = False

                dt = clock.tick(60) / 1000
        except KeyboardInterrupt:
            pass

        self.logger.debug("Shutting down!")

        pygame.quit()

        self.camera.destroy()
        self.input.destroy()
        self.ui.destroy()

        for x in self.objects:
            x.destroy()

        self.objects = []
