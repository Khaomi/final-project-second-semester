from __future__ import annotations

from src.static_config import SPRITE_LAYER
from src.objects.sprite import Sprite
from src.objects.belt import Belt
from typing import TYPE_CHECKING
from pygame import Vector2


if TYPE_CHECKING:
    from src.game import Game


class Item(Sprite):
    def __init__(
        self,
        game: Game,
        type: str = "unknown",
        position: Vector2 | None = None,
        size: Vector2 | None = None,
        rotation: int = 0,
    ):
        super().__init__(
            game,
            "assets/sprite/item.png",
            position,
            size,
            rotation,
            layer=SPRITE_LAYER.ITEM,
        )
        self.type = type
        self.belt: Belt | None = None
        self.despawn_timer = 0
        self.search_for_belt()
        self.game.on("update", self.update)

    def search_for_belt(self):
        if self.belt is not None:
            return

        grid_pos = (int(self.grid_position.x), int(self.grid_position.y))

        if grid_pos not in self.game.position_map:
            return

        for x in self.game.position_map[grid_pos]:
            if isinstance(x, Belt):
                x.insert_item(self)
                self.despawn_timer = 0

    def search_for_machine(self):
        grid_pos = (int(self.grid_position.x), int(self.grid_position.y))

        if grid_pos not in self.game.position_map:
            return

        for x in self.game.position_map[grid_pos]:
            print(x)
            pass
            # if isinstance(x, Machine):
            #     x.insert_item(self)
            #     self.despawn_timer = 0

    @Sprite.position.setter
    def position(self, value: Vector2):  # type: ignore
        Sprite.position.fset(self, value)  # type: ignore
        self._position = value
        self.search_for_belt()

    def update(self, dt: float):
        if self.belt:
            return

        self.despawn_timer += dt

        if self.despawn_timer >= 15:
            self.destroy()

    def destroy(self):
        self.game.remove_listener("update", self.update)
        super().destroy()
