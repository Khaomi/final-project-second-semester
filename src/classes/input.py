from __future__ import annotations

from src.objects import Machine, Belt, Item
from src.static_config import GRID_SIZE
from src.constants import (
    INPUT_DEFAULT_DIRECTION,
    INPUT_DEFAULT_MODE,
    INPUT_DIRECTION_MAX,
    INPUT_DIRECTION_MIN,
    INPUT_MODE_MAX,
    INPUT_MODE_MIN,
    INPUT_RECIPE_BOOK_VISIBLE_ITEMS,
    ZOOM_SCROLL_MULTIPLIER,
    ZOOM_KEYBOARD_STEP,
)
from src.machines import Seller, Miner
from typing import TYPE_CHECKING, Any
from src.classes import EventEmitter
from dataclasses import dataclass
from pygame import Vector2, mouse
import pygame

if TYPE_CHECKING:
    from src.game import Game


@dataclass
class SelectorOption:
    kind: str
    machine_type: str | None = None
    cost: int = 0


class Input(EventEmitter):
    def __init__(self, game: Game):
        super().__init__()

        self.game = game
        self.direction = INPUT_DEFAULT_DIRECTION
        self.mode = INPUT_DEFAULT_MODE
        self.selected_obj: SelectorOption | None = None

        self.start_pos: Vector2 | None = None
        self.cam_start_pos: Vector2 | None = None
        self.obj_start_pos: list[Any] | None = None

        self.recipe_book_open: bool = False
        self.recipe_book_machine_idx: int = 0
        self.recipe_book_scroll: int = 0

        self.selectors: list[SelectorOption] = [
            SelectorOption(kind="belt", cost=0),
            SelectorOption(
                kind="seller",
                cost=self.game.data.get_machine_data("seller")["cost"],
            ),
            SelectorOption(
                kind="miner",
                cost=self.game.data.get_machine_data("miner")["cost"],
            ),
        ]
        self.selectors.extend(
            SelectorOption(
                kind="machine",
                machine_type=x,
                cost=self.game.data.machine_data[x]["cost"],
            )
            for x in self.game.data.machine_data.keys()
            if x not in ["unknown", "miner", "seller"]
        )

        self.game.on(f"PYGAME_{pygame.MOUSEBUTTONUP}", self.__on_mouseup)
        self.game.on(f"PYGAME_{pygame.MOUSEBUTTONDOWN}", self.__on_mousedown)
        self.game.on(f"PYGAME_{pygame.MOUSEWHEEL}", self.__on_mousewheel)
        self.game.on(f"PYGAME_{pygame.MOUSEMOTION}", self.__on_mousemove)
        self.game.on(f"PYGAME_{pygame.KEYUP}", self.__on_keyup)
        self.game.on(f"PYGAME_{pygame.KEYDOWN}", self.__on_keydown)

    def __del__(self):
        self.destroy()

    ####

    @property
    def _rotation(self):
        return ((self.direction - 1) % 4) * 90

    @property
    def placement_rotation(self):
        return self._rotation

    def _sync_selector_rotation(self):
        pass

    def _grid_position_from_screen(self, pos: Vector2):
        world = self.game.camera.screen_to_world(pos)
        return (int(world.x // GRID_SIZE), int(world.y // GRID_SIZE))

    def _rotate_object_or_selection(self, grid_position: tuple[int, int]):
        if grid_position in self.game.position_map:
            for obj in self.game.position_map[grid_position]:
                if isinstance(obj, Item):
                    continue

                if hasattr(obj, "rotation"):
                    obj.rotation = (obj.rotation + 90) % 360
                return

        self.direction += 1
        if self.direction > INPUT_DIRECTION_MAX:
            self.direction = INPUT_DIRECTION_MIN
        if self.direction < 1:
            self.direction = 4

        self._sync_selector_rotation()

    def _build_selected_object(self, world_pos: Vector2):
        if self.selected_obj is None:
            return None

        if self.selected_obj.kind == "belt":
            obj = Belt(self.game, position=world_pos)
        elif self.selected_obj.kind == "seller":
            obj = Seller(self.game, position=world_pos)
        elif self.selected_obj.kind == "miner":
            obj = Miner(self.game, position=world_pos)
        else:
            obj = Machine(self.game, self.selected_obj.machine_type, position=world_pos)

        obj.rotation = self._rotation
        return obj

    def _remove_first_non_item(self, grid_position: tuple[int, int]):
        if grid_position not in self.game.position_map:
            return

        for obj in self.game.position_map[grid_position]:
            if isinstance(obj, Item):
                continue

            cost = getattr(obj, "cost", 0)
            self.game.data.cash += int(cost / 2)
            self.game.data.statistics.record_cash_earned(
                int(cost / 2),
                source="remove_refund",
            )
            obj.destroy()
            return

    def __on_mouseup(self, _: Any):
        if self.mode != 2:
            return

        mouse_pos = Vector2(mouse.get_pos())
        grid_position = self._grid_position_from_screen(mouse_pos)

        if self.obj_start_pos is not None:
            for obj in self.obj_start_pos:
                if isinstance(obj, Item):
                    continue

                obj.grid_position = Vector2(grid_position[0], grid_position[1])

            self.obj_start_pos = None
            return

        self.start_pos = None
        self.cam_start_pos = None

    def __on_mousemove(self, value: dict[str, Any]):
        # Key: Left click drag
        if self.mode != 2:
            return

        if self.start_pos is None or self.cam_start_pos is None:
            return

        pos = Vector2(value["pos"][0], value["pos"][1])
        self.game.camera.position = self.cam_start_pos - (
            (pos - self.start_pos) / self.game.camera.zoom
        )
        self.game.request_flip(False)

    def __on_mousewheel(self, value: dict[str, Any]):
        if self.recipe_book_open:
            machines = [k for k in self.game.data.machine_data.keys() if k != "unknown"]
            self.recipe_book_scroll = max(
                0,
                min(
                    len(machines) - 1, self.recipe_book_scroll - int(value.get("y", 0))
                ),
            )
            return

        delta = float(value.get("y", 0)) * ZOOM_SCROLL_MULTIPLIER
        if delta == 0:
            return

        self.game.camera.adjust_zoom(delta, Vector2(pygame.mouse.get_pos()))

    def __on_mousedown(self, value: dict[str, Any]):
        if value["button"] != 1:
            return

        # Key: Left click
        pos = Vector2(value["pos"][0], value["pos"][1])
        grid_position = self._grid_position_from_screen(pos)

        if self.recipe_book_open:
            machines = [k for k in self.game.data.machine_data.keys() if k != "unknown"]
            left_panel_x, left_panel_y, left_panel_w, item_h = 10, 40, 210, 40
            if (
                left_panel_x <= pos.x <= left_panel_x + left_panel_w
                and pos.y >= left_panel_y
            ):
                rel_y = pos.y - left_panel_y - 8
                clicked_idx = int(rel_y // item_h) + self.recipe_book_scroll
                if 0 <= clicked_idx < len(machines):
                    self.recipe_book_machine_idx = clicked_idx
            return

        if self.mode == 1:
            _, height = pygame.display.get_window_size()
            y = height - 16 - GRID_SIZE

            max_x = len(self.selectors) * GRID_SIZE
            if y <= pos.y < y + GRID_SIZE and pos.x < max_x:
                index = int(pos.x // GRID_SIZE)
                if index < len(self.selectors):
                    self.selected_obj = self.selectors[index]
                return

            if self.selected_obj is None:
                return

            if grid_position in self.game.position_map:
                for obj in self.game.position_map[grid_position]:
                    if not isinstance(obj, Item):
                        return

            cost = self.selected_obj.cost
            if cost > self.game.data.cash:
                return

            world = self.game.camera.screen_to_world(pos)
            obj = self._build_selected_object(world)
            if obj is None:
                return

            obj.snap_to_grid()
            self.game.objects.append(obj)
            self.game.data.cash -= cost
            self.game.data.statistics.record_cash_spent(cost, source="place_object")
        elif self.mode == 2:
            if grid_position not in self.game.position_map:
                self.start_pos = pos
                self.cam_start_pos = self.game.camera.position
            else:
                self.obj_start_pos = list(self.game.position_map[grid_position])
        elif self.mode == 3:
            self._remove_first_non_item(grid_position)

    def __on_keyup(self, value: dict[str, Any]):
        pass

    def __on_keydown(self, value: dict[str, Any]):
        if value["key"] == pygame.K_TAB:
            self.recipe_book_open = not self.recipe_book_open
            return

        if self.recipe_book_open:
            machines = [k for k in self.game.data.machine_data.keys() if k != "unknown"]
            visible_count = INPUT_RECIPE_BOOK_VISIBLE_ITEMS
            if value["key"] == pygame.K_UP:
                self.recipe_book_machine_idx = max(0, self.recipe_book_machine_idx - 1)
            elif value["key"] == pygame.K_DOWN:
                self.recipe_book_machine_idx = min(
                    len(machines) - 1, self.recipe_book_machine_idx + 1
                )
            if self.recipe_book_machine_idx < self.recipe_book_scroll:
                self.recipe_book_scroll = self.recipe_book_machine_idx
            elif (
                self.recipe_book_machine_idx >= self.recipe_book_scroll + visible_count
            ):
                self.recipe_book_scroll = (
                    self.recipe_book_machine_idx - visible_count + 1
                )
            return

        if value["key"] in [pygame.K_EQUALS, pygame.K_KP_PLUS]:
            self.game.camera.adjust_zoom(ZOOM_KEYBOARD_STEP)

        if value["key"] in [pygame.K_MINUS, pygame.K_KP_MINUS]:
            self.game.camera.adjust_zoom(-ZOOM_KEYBOARD_STEP)

        if value["key"] == 114:
            mouse_pos = Vector2(mouse.get_pos())
            grid_position = self._grid_position_from_screen(mouse_pos)
            self._rotate_object_or_selection(grid_position)

        if value["key"] == 100:
            setattr(self.game, "DEBUG", not bool(self.game.DEBUG))

        if value["key"] == 109:
            self.mode += 1

            if self.mode > INPUT_MODE_MAX:
                self.mode = INPUT_MODE_MIN
            if self.mode < INPUT_MODE_MIN:
                self.mode = INPUT_MODE_MAX

            if self.mode == 1:
                self.selected_obj = (
                    self.selectors[0] if len(self.selectors) > 0 else None
                )
                self._sync_selector_rotation()
            else:
                self.selected_obj = None

        # Key: 1-9
        if 49 <= value["key"] <= 57:
            if self.mode != 1:
                return

            idx = value["key"] - 49
            if idx + 1 > len(self.selectors):
                return

            self.selected_obj = self.selectors[idx]
            self._sync_selector_rotation()

    def destroy(self):
        self.game.remove_listener(f"PYGAME_{pygame.MOUSEBUTTONUP}", self.__on_mouseup)
        self.game.remove_listener(
            f"PYGAME_{pygame.MOUSEBUTTONDOWN}", self.__on_mousedown
        )
        self.game.remove_listener(f"PYGAME_{pygame.MOUSEWHEEL}", self.__on_mousewheel)
        self.game.remove_listener(f"PYGAME_{pygame.MOUSEMOTION}", self.__on_mousemove)
        self.game.remove_listener(f"PYGAME_{pygame.KEYUP}", self.__on_keyup)
        self.game.remove_listener(f"PYGAME_{pygame.KEYDOWN}", self.__on_keydown)
        self.remove_all_listeners()
