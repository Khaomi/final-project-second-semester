from objects.machine import Machine


class Miner(Machine):
    def __init__(self, game, pos=(0, 0), ore_type="copper", last_drop=0):
        super().__init__(
            game,
            "miner",
            pos,
        )
        self.ore_type = ore_type
        self.last_drop = last_drop

    def update(self, dt, events):
        super().update(dt, events)
        self.last_drop += dt / 1000

        if self.last_drop >= 3:
            self.output_item(self.ore_type + "_ore")
            self.last_drop = 0

    def to_dict(self):
        obj = super().to_dict()
        obj["type"] = "miner"
        del obj["inventory"]
        return obj

    @staticmethod
    def from_dict(game, data: dict):
        instance = Miner(
            game,
            pos=data.get("position", (0, 0)),
            ore_type=data.get("ore_type", "copper"),
            last_drop=data.get("last_drop", 0),
        )
        instance.direction = data.get("direction", 1)
        return instance
