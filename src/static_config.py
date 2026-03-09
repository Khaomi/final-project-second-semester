from __future__ import annotations

from enum import IntEnum


class DIRECTION(IntEnum):
    FORWARD = 0
    LEFT = 1
    BACKWARD = 2
    RIGHT = 3


def rotate_90(v: tuple[int, int]):
    x, y = v
    return (y, -x)


DIRECTION_VECTORS = {
    DIRECTION.FORWARD: (0, 1),
    DIRECTION.LEFT: (-1, 0),
    DIRECTION.BACKWARD: (0, -1),
    DIRECTION.RIGHT: (1, 0),
}

ROTATION_DIRECTION_VECTOR: dict[int, dict[DIRECTION, tuple[int, int]]] = {}

for angle in (0, 90, 180, 270):
    rotations = angle // 90
    ROTATION_DIRECTION_VECTOR[angle] = {}

    for direction, vec in DIRECTION_VECTORS.items():
        rotated = vec
        for _ in range(rotations):
            rotated = rotate_90(rotated)

        ROTATION_DIRECTION_VECTOR[angle][direction] = rotated


class SPRITE_LAYER(IntEnum):
    BG = 0
    GRID = 1
    DEFAULT = 2
    TILE = 3
    ITEM = 4
    DEBUG = 5
    UI = 6


GRID_SIZE = 64
# FOR TESTING PURPOSE.
CULLING_DISABLED = False
