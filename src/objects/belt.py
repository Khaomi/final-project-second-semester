from __future__ import annotations

from src.static_config import DIRECTION, GRID_SIZE
from src.objects.sprite import Sprite
from typing import TYPE_CHECKING
from pygame import Vector2, math


if TYPE_CHECKING:
    from src.objects.item import Item
    from src.game import Game


class Belt(Sprite):
    def __init__(
        self,
        game: Game,
        position: Vector2 | None = None,
        size: Vector2 | None = None,
        rotation: int = 0,
    ):
        super().__init__(game, "assets/sprite/belt.png", position, size, rotation)

        self.next: Belt | None = None
        self.prev: Belt | None = None

        self.speed = 1
        self.item_progess: dict[Item, float] = {}
        self.__item_start_pos: dict[Item, Vector2] = {}

        self.__link_belt_list()

    @Sprite.rotation.setter
    def rotation(self, value: int):  # type: ignore
        self.__unlink_belt_list()
        Sprite.rotation.fset(self, value)  # type: ignore
        for item in self.item_progess:
            self.item_progess[item] = 0
        for item in self.__item_start_pos:
            self.__item_start_pos[item] = item.position.copy()

        self.__link_belt_list()

    @Sprite.position.setter
    def position(self, value: Vector2):  # type: ignore
        self.__unlink_belt_list()
        Sprite.position.fset(self, value)  # type: ignore
        self.__link_belt_list()

    def __link_belt_list(self):
        forward, backward = self.get_grid_forward(), self.get_grid_backward()
        forward = (int(forward.x), int(forward.y))
        backward = (int(backward.x), int(backward.y))

        if forward in self.game.position_map:
            belt = None

            for obj in self.game.position_map[forward]:
                if not isinstance(obj, Belt):
                    continue

                belt = obj
                break

            if belt:
                belt.prev = self
                self.next = belt

        if backward in self.game.position_map:
            belt = None

            for obj in self.game.position_map[backward]:
                if not isinstance(obj, Belt):
                    continue

                belt = obj
                break

            if belt:
                belt.next = self
                self.prev = belt

    def __unlink_belt_list(self):
        if self.prev:
            self.prev.next = None
            self.prev = None

        if self.next:
            self.next.prev = None
            self.next = None

    def destroy(self):
        self.__unlink_belt_list()
        super().destroy()

    ##

    def insert_item(self, item: Item):
        if item.belt:
            return

        item.belt = self
        self.item_progess[item] = 0
        self.__item_start_pos[item] = item.position.copy()

    def remove_item(self, item: Item):
        if item.belt != self:
            return
        item.belt = None
        del self.item_progess[item]
        del self.__item_start_pos[item]

    def update(self, dt: float):
        super().update(dt)

        rotation_vector = self.get_rotation_vector(DIRECTION.FORWARD)

        for item in list(self.item_progess):
            self.item_progess[item] += dt * self.speed

            progress = min(self.item_progess[item], 1)

            start_pos = self.__item_start_pos[item]
            target_x, target_y = (
                start_pos.x + (rotation_vector[0] * GRID_SIZE),
                start_pos.y + (rotation_vector[1] * GRID_SIZE),
            )
            item.position = Vector2(
                math.lerp(start_pos.x, target_x, progress),
                math.lerp(start_pos.y, target_y, progress),
            )

            if self.item_progess[item] >= 1:
                self.remove_item(item)
                if self.next:
                    self.next.insert_item(item)
