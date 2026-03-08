from __future__ import annotations

from enum import IntEnum


class SPRITE_LAYER(IntEnum):
    BG = 0
    GRID = 1
    DEFAULT = 2
    TILE = 3
    DEBUG = 4
    UI = 5


GRID_SIZE = 64
# FOR TESTING PURPOSE.
CULLING_DISABLED = False
