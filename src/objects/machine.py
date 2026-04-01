from __future__ import annotations


from typing import TYPE_CHECKING, Any, cast
from src.static_config import SPRITE_LAYER
from src.objects.sprite import Sprite
from src.classes.data import Data
from src.objects.item import Item
from pygame import Vector2

if TYPE_CHECKING:
    from src.classes.data import MachineData
    from src.game import Game


class Machine(Sprite):
    def __init__(
        self,
        game: Game,
        type: str | None = "unknown",
        data: MachineData | None = None,
        position: Vector2 | None = None,
        size: Vector2 | None = None,
        rotation: int = 0,
    ):
        self.type = type

        if data is None and type is None:
            raise ValueError("Invalid options! Choose either `type` or `data`")

        data = data if data is not None else Data.get_machine_data(type)

        super().__init__(
            game, data["sprite"], position, size, rotation, SPRITE_LAYER.TILE
        )

        self.type = data["type"]
        self.cost = data["cost"]
        self.recipes = data["recipes"]

        self.inventory: dict[str, int] = {}
        self._active_recipe: int | None = None
        self._selected_recipe_index: int | None = None
        self.timer = 0

        self.game.add_listener("update", self.update)
        self._absorb_items_on_tile()

    def __del__(self):
        self.destroy()

    ####

    def _absorb_items_on_tile(self):
        grid_pos = (int(self.grid_position.x), int(self.grid_position.y))
        if grid_pos not in self.game.position_map:
            return

        for obj in list(self.game.position_map[grid_pos]):
            if not isinstance(obj, Item) or obj.destroyed:
                continue

            self.insert_item(obj.type)
            obj.destroy()

    def __process_recipes(
        self,
    ):
        if self._active_recipe is not None:
            return

        recipe_order = list(range(len(self.recipes)))
        if self._selected_recipe_index is not None:
            recipe_order = [self._selected_recipe_index]

        for idx in recipe_order:
            recipe = self.recipes[idx]
            passed = True

            for x in recipe["inputs"]:
                if x["type"] not in self.inventory:
                    passed = False
                    break

                if self.inventory[x["type"]] < x["amount"]:
                    passed = False
                    break

            if not passed:
                continue

            self._active_recipe = idx
            break

    def __consume_recipe(self):
        if self._active_recipe is None:
            return

        recipe_index = self._active_recipe
        recipe = self.recipes[recipe_index]
        inputs: list[str] = []
        outputs: list[str] = []

        for inp in recipe["inputs"]:
            self.inventory[inp["type"]] -= inp["amount"]
            if self.inventory[inp["type"]] <= 0:
                del self.inventory[inp["type"]]

            for _ in range(inp["amount"]):
                inputs.append(inp["type"])

        for out in recipe["outputs"]:
            for _ in range(out["amount"]):
                self.output_item(out["type"])
                outputs.append(out["type"])

        self.game.data.statistics.record_machine_process(
            machine_type=str(self.type),
            recipe_index=recipe_index,
            inputs=inputs,
            outputs=outputs,
        )

        self._active_recipe = None
        self.__process_recipes()

    def set_selected_recipe(self, recipe_index: int | None):
        if recipe_index is not None:
            if recipe_index < 0 or recipe_index >= len(self.recipes):
                return

        self._selected_recipe_index = recipe_index
        self._active_recipe = None
        self.timer = 0
        self.__process_recipes()

    def get_selected_recipe(self) -> int | None:
        return self._selected_recipe_index

    def insert_item(self, type: str):
        if type not in self.inventory:
            self.inventory[type] = 0

        self.inventory[type] += 1
        self.__process_recipes()

    def output_item(self, type: str):
        item = Item(self.game, position=self.get_forward(), type=type)
        self.game.objects.append(item)

    def update(self, dt: float):
        if self._active_recipe is None:
            return

        self.timer += dt

        recipe = self.recipes[self._active_recipe]
        if self.timer < recipe["duration"]:
            return

        self.timer = 0
        self.__consume_recipe()

    def destroy(self):
        self.game.remove_listener("update", self.update)
        super().destroy()

    # Serialization

    def to_dict(self) -> dict[str, Any]:
        return {
            "class": "machine",
            "machine_type": self.type,
            "position": (int(self.position.x), int(self.position.y)),
            "rotation": int(self.rotation),
            "inventory": self.inventory,
            "selected_recipe": self._selected_recipe_index,
        }

    @classmethod
    def from_dict(cls, game: Game, data: dict[str, Any]):
        pos = data.get("position", [0, 0])
        obj = cls(
            game,
            type=str(data.get("machine_type", data.get("type", "unknown"))),
            position=Vector2(pos[0], pos[1]),
            rotation=int(data.get("rotation", 0)),
        )
        inventory = data.get("inventory", {})
        if isinstance(inventory, dict):
            parsed_inventory: dict[str, int] = {}
            inventory_dict = cast(dict[Any, Any], inventory)
            for key, value in inventory_dict.items():
                parsed_inventory[str(key)] = int(value) if isinstance(value, int) else 0
            obj.inventory = parsed_inventory

        selected_recipe = data.get("selected_recipe")
        if isinstance(selected_recipe, int):
            obj.set_selected_recipe(selected_recipe)
        else:
            obj.set_selected_recipe(None)
        return obj
