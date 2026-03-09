from __future__ import annotations

from src.static_config import SPRITE_LAYER, GRID_SIZE, CULLING_DISABLED
from src.classes.game_object import GameObject
from pygame import Vector2, image, transform
from pygame.sprite import DirtySprite
from typing import TYPE_CHECKING
from pygame.rect import Rect

if TYPE_CHECKING:
    from pygame.typing import FileLike
    from src.game import Game


class GameObjectDirtySprite(DirtySprite):
    def __init__(
        self,
        game: Game,
        position: Vector2 | None = None,
        size: Vector2 | None = None,
        rotation: int = 0,
        *groups,  # type: ignore
    ):

        super().__init__(groups)  # type: ignore
        self.game = game
        self._position = position if position else Vector2(0, 0)
        self._size = size if size else Vector2(1, 1)
        self._rotation = rotation % 360
        self._active = True

        self.game.camera.on("resize", self.__update_visibility)
        self.game.camera.on("move", self.__update_visibility)
        self.__update_visibility()

    def __update_visibility(self):
        world_rect = Rect(
            self._position.x,
            self._position.y,
            self.size.x * GRID_SIZE,
            self.size.y * GRID_SIZE,
        )
        self._visible = CULLING_DISABLED or (
            self._active and self.game.camera.is_in_camera(world_rect)
        )
        self.dirty = 1

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value: bool):
        self._active = value
        self.dirty = 1
        self.__update_visibility()

    @property
    def rect(self) -> Rect:  # type: ignore
        pos = self.game.camera.world_to_screen(self.position)
        return Rect(pos.x, pos.y, self._size.x * GRID_SIZE, self._size.y * GRID_SIZE)

    @property
    def visible(self) -> int:  # type: ignore
        return self._active and self._visible and 1 or 0

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value: Vector2):
        self._position = value
        self.__update_visibility()

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value: Vector2):
        self._size = value
        self.__update_visibility()

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value: int):
        self._rotation = value
        self.__update_visibility()

    def should_cull(self):
        return not CULLING_DISABLED and (
            not self._active
            or not self.game.camera.is_in_camera(
                (
                    self._position.x,
                    self._position.y,
                    self._size.x * GRID_SIZE,
                    self._size.y * GRID_SIZE,
                )
            )
        )

    def destroy(self):
        self.game.camera.remove_listener("resize", self.__update_visibility)
        self.game.camera.remove_listener("move", self.__update_visibility)


class Sprite(GameObject):
    def __init__(
        self,
        game: Game,
        file: FileLike,
        position: Vector2 | None = None,
        size: Vector2 | None = None,
        rotation: int = 0,
        layer: SPRITE_LAYER = SPRITE_LAYER.DEFAULT,
    ):
        self.game = game
        self.sprite = GameObjectDirtySprite(
            self.game, position=position, size=size, rotation=rotation
        )

        self._base_image = image.load(file).convert_alpha()
        self.sprite.image = transform.rotate(self._base_image, self.sprite.rotation)

        self.game.sprite_layers.add(self.sprite, layer=layer)
        super().__init__(game, position, size, rotation)

    @property
    def active(self):
        return self.sprite.active

    @active.setter
    def active(self, value: bool):
        self.sprite.active = value

    @property
    def visible(self):
        return self.sprite.visible == 1

    @visible.setter
    def visible(self, value: bool):  # type: ignore
        pass

    @property
    def position(self):
        return self.sprite.position

    @position.setter
    def position(self, value: Vector2):
        self._update_position_map(value, self.sprite.position)
        self.sprite.position = value

    @property
    def rotation(self) -> int:
        return self.sprite.rotation

    @rotation.setter
    def rotation(self, value: int):
        value = value % 360
        self.sprite.rotation = value
        self.sprite.image = transform.rotate(self._base_image, value)
        self.sprite.dirty = 1

    @property
    def size(self) -> Vector2:
        return self.sprite.size

    @size.setter
    def size(self, value: Vector2):
        self.sprite.size = value

    def destroy(self):
        self.game.sprite_layers.remove(self.sprite)
        self.sprite.destroy()
        super().destroy()
