from objects.engines.camera import Camera
from objects.engines.input import Input
from objects.belt import Belt
from objects.item import Item
from objects.machine import Machine
from objects.machines.miner import Miner
from objects.machines.seller import Seller
from typing import TYPE_CHECKING, List, Dict, Tuple
from objects.engines.ui import UI
from .statistics import Statistics
import pygame
import time
import math
import json
from pathlib import Path
import marshal

if TYPE_CHECKING:
    from objects.game_object import GameObject


class Game:
    SIZE_PER_TILE = 64
    DEBUG = False

    FONTS: Dict[str, pygame.Font] = {}

    CLASS_MAPPINGS = {
        "belt": Belt,
        "item": Item,
        "machine": Machine,
        "seller": Seller,
        "miner": Miner,
    }

    def __init__(self):
        pygame.init()

        self.FONTS["Arial"] = pygame.font.SysFont("Arial", 18)
        self.FONTS["Comic Sans MS"] = pygame.font.SysFont("Comic Sans MS", 18)

        pygame.display.set_caption("Funky Factory Game")
        pygame.display.set_icon(self.FONTS["Arial"].render("FFG", True, "White"))

        self.screen = pygame.display.set_mode((1280, 720))
        self.cash = 0

        self.statistics = Statistics()
        self.ui = UI(self)
        self.input = Input(self)
        self.camera = Camera(self)

        self.objects: List[GameObject] = [self.camera, self.ui, self.input]
        self.start_time = math.floor(time.time())

        self.position_map: Dict[Tuple[int, int], List[GameObject]] = {}

        if not self.load_game("save"):
            pass

    def save_game(self, filename: str):
        filename = f"{filename}.data" if not self.DEBUG else f"{filename}.json"

        save_data = {
            "cash": self.cash,
            "objects": [],
        }

        for obj in self.objects:
            if obj in [self.input, self.camera, self.ui]:
                continue

            obj_data = obj.to_dict()
            if obj_data is not None:
                save_data["objects"].append(obj_data)

        path = Path.cwd() / filename
        if self.DEBUG:
            with open(path, "wt", encoding="utf-8") as f:
                json.dump(save_data, f)
        else:
            with open(path, "wb") as f:
                marshal.dump(save_data, f)

    def load_game(self, filename: str) -> bool:
        save_data = None

        if (Path.cwd() / (filename + ".data")).exists():
            try:
                with open(Path.cwd() / (filename + ".data"), "rb") as f:
                    save_data = marshal.load(f)
            except Exception as e:
                print(e)

        if save_data is None and (Path.cwd() / (filename + ".json")).exists():
            try:
                with open(Path.cwd() / (filename + ".json"), "rt") as f:
                    save_data = json.load(f)
            except Exception as e:
                print(e)

        if save_data is None:
            save_data = {}

        self.cash = save_data.get("cash", 11)
        self.objects = [self.input, self.camera, self.ui]
        for obj_data in save_data.get("objects", []):
            obj_type = obj_data.get("type")
            obj = None

            if obj_type in self.CLASS_MAPPINGS:
                obj = self.CLASS_MAPPINGS[obj_type].from_dict(self, obj_data)

            if obj:
                obj.add_to_game()
                if obj_type != "item":
                    obj.snap_to_grid()
        return True

    def add_object(self, obj: GameObject):
        self.objects.append(obj)

    def remove_object(self, obj: GameObject):
        if obj in self.objects:
            self.objects.remove(obj)

        if obj.grid_position not in self.position_map:
            return

        if obj in self.position_map[obj.grid_position]:
            self.position_map[obj.grid_position].remove(obj)
        if len(self.position_map[obj.grid_position]) <= 0:
            del self.position_map[obj.grid_position]

    def add_cash(self, amount):
        if amount <= 0:
            return
        self.cash += amount
        self.statistics.increment("cash_earned", amount)

    def remove_cash(self, amount):
        if amount <= 0:
            return 0
        removed = min(self.cash, amount)
        self.cash -= removed
        return removed

    def start(self):
        try:
            is_running = True
            clock = pygame.Clock()
            dt = 0

            while is_running:
                self.screen.fill("black")

                events = pygame.event.get()

                for x in events:
                    if x.type == pygame.QUIT:
                        is_running = False
                        break

                if not is_running:
                    break

                for object in self.objects:
                    object.update(dt, events)

                for object in self.objects:
                    if object.force_render or self.camera.is_in_camera_view(
                        object.position
                    ):
                        object.render(self.screen)

                pygame.display.flip()
                dt = clock.tick(60)
        except KeyboardInterrupt:
            pass

        pygame.quit()
        self.save_game("save")
        self.statistics.increment("playtime", math.floor(time.time()) - self.start_time)
        self.statistics.save_data("statistics.json")
