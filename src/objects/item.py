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
        self.belt: Belt | None = None
        self.__search_for_belt()

    def __search_for_belt(self):
        if self.belt is not None:
            return

        grid_pos = (int(self.grid_position.x), int(self.grid_position.y))

        if grid_pos not in self.game.position_map:
            return

        for x in self.game.position_map[grid_pos]:
            if isinstance(x, Belt):
                x.insert_item(self)

    @Sprite.position.setter
    def position(self, value: Vector2):  # type: ignore
        Sprite.position.fset(self, value)  # type: ignore
        self.__search_for_belt()
