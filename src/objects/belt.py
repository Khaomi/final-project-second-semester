from __future__ import annotations


from src.static_config import DIRECTION, GRID_SIZE
from typing import TYPE_CHECKING, Any
from src.objects.sprite import Sprite
from pygame import Vector2, math

if TYPE_CHECKING:
    from src.game import Game
    from src.objects.item import Item


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
        self.prevs: list[Belt] = []

        self.speed = 1
        self.item_progress: dict[Item, float] = {}
        self.__item_start_center: dict[Item, Vector2] = {}

        self.__link_belt_list()

        self.game.on("update", self.update)

    def __del__(self):
        self.destroy()

    ####

    @Sprite.rotation.setter
    def rotation(self, value: int):  # type: ignore
        value = value % 360
        self.__unlink_belt_list()
        Sprite.rotation.fset(self, value)  # type: ignore
        self._rotation = value
        for item in self.item_progress:
            self.item_progress[item] = 0
        for item in self.__item_start_center:
            self.__item_start_center[item] = self.__item_center(item)

        self.__link_belt_list()

    @Sprite.position.setter
    def position(self, value: Vector2):  # type: ignore
        self.__unlink_belt_list()
        Sprite.position.fset(self, value)  # type: ignore
        self._position = value
        self.__link_belt_list()
        self.search_for_item()

    def __link_belt_list(self):
        current = (int(self.grid_position.x), int(self.grid_position.y))
        forward = self.get_grid_forward()
        forward = (int(forward.x), int(forward.y))
        neighbors = (
            self.get_grid_left(),
            self.get_grid_right(),
            self.get_grid_backward(),
            self.get_grid_forward(),
        )

        if forward in self.game.position_map:
            belt = None

            for obj in self.game.position_map[forward]:
                if not isinstance(obj, Belt):
                    continue
                if obj is self:
                    continue

                belt = obj
                break

            if belt:
                if self not in belt.prevs:
                    belt.prevs.append(self)
                self.next = belt

        for neighbor in neighbors:
            neighbor_pos = (int(neighbor.x), int(neighbor.y))
            if neighbor_pos not in self.game.position_map:
                continue

            belt = None
            for obj in self.game.position_map[neighbor_pos]:
                if not isinstance(obj, Belt):
                    continue
                if obj is self:
                    continue
                if obj.destroyed:
                    continue

                obj_forward = obj.get_grid_forward()
                if (int(obj_forward.x), int(obj_forward.y)) != current:
                    continue

                belt = obj
                break

            if belt:
                if belt not in self.prevs:
                    self.prevs.append(belt)
                belt.next = self

    def __unlink_belt_list(self):
        for prev_belt in self.prevs:
            if prev_belt.next is self:
                prev_belt.next = None
        self.prevs = []

        if self.next:
            if self in self.next.prevs:
                self.next.prevs.remove(self)
            self.next = None

    def destroy(self):
        self.game.remove_listener("update", self.update)
        self.__unlink_belt_list()
        super().destroy()

    def to_dict(self) -> dict[str, Any]:
        return {
            "class": "belt",
            "position": [int(self.position.x), int(self.position.y)],
            "rotation": int(self.rotation),
        }

    @classmethod
    def from_dict(cls, game: Game, data: dict[str, Any]):
        pos = data.get("position", [0, 0])
        return cls(
            game,
            position=Vector2(pos[0], pos[1]),
            rotation=int(data.get("rotation", 0)),
        )

    ##

    def __item_center(self, item: Item) -> Vector2:
        half_size = item.absolute_size / 2
        return Vector2(item.position.x + half_size.x, item.position.y + half_size.y)

    def __center_to_item_pos(self, item: Item, center: Vector2) -> Vector2:
        half_size = item.absolute_size / 2
        return Vector2(center.x - half_size.x, center.y - half_size.y)

    def __belt_center(self) -> Vector2:
        half = GRID_SIZE / 2
        return Vector2(self.position.x + half, self.position.y + half)

    def search_for_item(self):
        from src.objects.item import Item

        grid_pos = (int(self.grid_position.x), int(self.grid_position.y))

        if grid_pos not in self.game.position_map:
            return

        for x in self.game.position_map[grid_pos]:
            if isinstance(x, Item) and not x.destroyed:
                self.insert_item(x)

    def insert_item(self, item: Item, initial_progress: float = 0):
        if item.belt:
            return

        item.belt = self
        item.despawn_timer = 0
        self.item_progress[item] = max(0.0, initial_progress)
        self.__item_start_center[item] = self.__item_center(item)

    def remove_item(self, item: Item):
        if item.belt != self:
            return
        item.belt = None
        del self.item_progress[item]
        del self.__item_start_center[item]

    def update(self, dt: float):
        rotation_vector = self.get_rotation_vector(DIRECTION.FORWARD)

        for item in list(self.item_progress):
            if item.destroyed:
                self.remove_item(item)
                continue

            self.item_progress[item] += dt * self.speed

            progress = min(self.item_progress[item], 1)

            start_center = self.__item_start_center[item]
            belt_center = self.__belt_center()
            target_center = Vector2(
                belt_center.x + (rotation_vector[0] * GRID_SIZE),
                belt_center.y + (rotation_vector[1] * GRID_SIZE),
            )
            lerped_center = Vector2(
                math.lerp(start_center.x, target_center.x, progress),
                math.lerp(start_center.y, target_center.y, progress),
            )
            item.position = self.__center_to_item_pos(item, lerped_center)

            if self.item_progress[item] >= 1:
                overflow = self.item_progress[item] - 1
                self.remove_item(item)
                if self.next:
                    self.next.insert_item(item, initial_progress=overflow)
                else:
                    item.search_for_machine()
                    if not item.destroyed:
                        item.search_for_belt()
