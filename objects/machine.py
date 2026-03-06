from objects.sprite import Sprite
from objects.item import Item
from pathlib import Path
import json


class Machine(Sprite):
    _MACHINE_CONFIG = None

    @staticmethod
    def _load_machine_config():
        if Machine._MACHINE_CONFIG is not None:
            return Machine._MACHINE_CONFIG

        path = Path.cwd() / "assets" / "machines.json"
        if not path.exists():
            Machine._MACHINE_CONFIG = {}
            return Machine._MACHINE_CONFIG

        try:
            with open(path, "r") as f:
                Machine._MACHINE_CONFIG = json.load(f)
        except (OSError, json.JSONDecodeError):
            Machine._MACHINE_CONFIG = {}

        return Machine._MACHINE_CONFIG

    @staticmethod
    def machine_data_from_id(machine_id):
        machine_config = Machine._load_machine_config()
        return machine_config.get(machine_id, {})

    @staticmethod
    def sprite_from_machine_id(machine_id):
        machine_data = Machine.machine_data_from_id(machine_id)
        return machine_data.get("sprite", f"assets/machines/{machine_id}.png")

    @staticmethod
    def recipes_from_machine_id(machine_id):
        machine_data = Machine.machine_data_from_id(machine_id)
        recipes = machine_data.get("recipes")
        if isinstance(recipes, list):
            return recipes
        return None

    @staticmethod
    def cost_from_machine_id(machine_id):
        machine_data = Machine.machine_data_from_id(machine_id)
        cost = machine_data.get("cost", 9999999999999)
        try:
            return int(cost)
        except (TypeError, ValueError):
            return 9999999999999

    def __init__(self, game, machine_id="unknown", pos=(0, 0), recipes=None, cost=None):
        super().__init__(
            game, self.sprite_from_machine_id(machine_id), pos, text_label=machine_id
        )
        self.machine_id = machine_id
        self.recipes = recipes or self.recipes_from_machine_id(self.machine_id)
        self.cost = cost or self.cost_from_machine_id(self.machine_id)
        self.inventory = {}

    def insert_item(self, obj: Item):
        item_id = obj.item_id

        if item_id not in self.inventory:
            self.inventory[item_id] = 0

        self.inventory[item_id] += 1
        obj.remove_from_game()

        recipes = self.recipes
        for x in recipes:
            input = x["input"]
            output = x["output"]

            skip = False

            for x in input:
                if x["item-id"] not in self.inventory:
                    skip = True
                    break

                if self.inventory[x["item-id"]] < x.get("amount", 1):
                    skip = True
                    break

            if skip:
                continue

            for x in input:
                self.inventory[x["item-id"]] -= x.get("amount", 1)
                if self.inventory[x["item-id"]] <= 0:
                    del self.inventory[x["item-id"]]

            for x in output:
                for _ in range(x.get("amount", 1)):
                    self.output_item(x["item-id"])

    def check_for_item(self):
        if self.grid_position not in self.game.position_map:
            return

        for x in self.game.position_map[self.grid_position]:
            if not isinstance(x, Item):
                continue
            self.insert_item(x)

    def output_item(self, item_id):
        output_item = Item(self.game, item_id)
        output_item.set_position(self.grid_to_world(self.get_forward()))
        output_item.add_to_game()

    def move(self, position):
        super().move(position)
        self.check_for_item()

    def render(self, screen):
        super().render(screen)

        if not self.game.DEBUG:
            return

        parts = [
            f"{item_id}:{count}" for item_id, count in sorted(self.inventory.items())
        ]
        items_text = "{" + ",".join(parts) + "}"
        text_surface = self.game.FONTS["Arial"].render(
            items_text, True, (255, 255, 255)
        )
        text_rect = text_surface.get_rect(
            center=self.world_to_camera((self.position[0], self.position[1] - 40))
        )
        screen.blit(text_surface, text_rect)

    def to_dict(self):
        data = super().to_dict()
        data["type"] = "machine"
        data["machine_id"] = self.machine_id
        data["inventory"] = self.inventory
        return data

    @staticmethod
    def from_dict(game, data):
        machine_id = data.get("machine_id") or "unknown"

        instance = Machine(
            game,
            pos=data.get("position", (0, 0)),
            machine_id=machine_id,
        )
        instance.direction = data.get("direction", 1)

        inventory = data.get("inventory", {})
        if isinstance(inventory, dict):
            instance.inventory.update(inventory)

        return instance
