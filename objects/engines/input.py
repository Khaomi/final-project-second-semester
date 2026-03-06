from objects.item import Item
from objects.machine import Machine
from objects.machines.miner import Miner
from objects.machines.seller import Seller
from objects.game_object import GameObject
from objects.belt import Belt
import pygame


class Input(GameObject):
    def __init__(self, game):
        super().__init__(game)
        self.direction = 1
        self.selected_obj = None
        # TODO: Enum
        # 1 - Select, 2 - Move, 3 - Remove
        self.mode = 2
        self.start_pos = None
        self.cam_start_pos = None
        self.obj_start_pos = None
        self.force_render = True

        self.selectors = [
            Belt(self.game),
            Seller(self.game),
            Miner(self.game),
        ]
        self.selectors.extend(
            Machine(self.game, x)
            for x in Machine._MACHINE_CONFIG.keys()
            if x not in ["unknown", "miner", "seller"]
        )

        {}.keys

    def update(self, dt, events):
        super().update(dt, events)

        absolute_mouse_pos = pygame.mouse.get_pos()
        mouse_pos = self.game.camera.to_world_position(absolute_mouse_pos)
        grid_position = (
            mouse_pos[0] // self.game.SIZE_PER_TILE,
            mouse_pos[1] // self.game.SIZE_PER_TILE,
        )

        for event in events:
            if event.type == pygame.KEYDOWN:
                print(event.dict)

                if event.dict["key"] == 114:
                    skip = False
                    if grid_position in self.game.position_map:
                        for x in self.game.position_map[grid_position]:
                            if isinstance(x, Item):
                                continue

                            x.direction += 1
                            if x.direction > 4:
                                x.direction = 1
                            elif x.direction < 1:
                                x.direction = 4

                            skip = True

                    if skip:
                        continue

                    self.direction += 1
                    if self.direction > 4:
                        self.direction = 1
                    if self.direction < 1:
                        self.direction = 4
                    for x in self.selectors:
                        x.direction = self.direction

                    if self.selected_obj:
                        self.selected_obj.direction = self.direction

                if event.dict["key"] == 100:
                    self.game.DEBUG = not self.game.DEBUG

                if event.dict["key"] == 109:
                    self.mode += 1

                    if self.mode > 3:
                        self.mode = 1
                    if self.mode < 1:
                        self.mode = 3

                    if self.mode == 1:
                        self.selected_obj = Belt(self.game)
                    else:
                        self.selected_obj = None

                if event.dict["key"] >= 49 and event.dict["key"] <= 57:
                    if self.mode != 1:
                        continue

                    idx = event.dict["key"] - 49
                    if idx + 1 > len(self.selectors):
                        continue

                    self.selected_obj = self.selectors[idx]
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.mode == 2:
                    if self.obj_start_pos is not None:
                        for x in self.obj_start_pos:
                            if isinstance(x, Item):
                                continue
                            x.move(x.grid_to_world(grid_position))
                        self.obj_start_pos = None
                    else:
                        self.start_pos = None
                        self.cam_start_pos = None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.mode == 1:
                    _, height = pygame.display.get_window_size()
                    y = height - 16 - self.game.SIZE_PER_TILE

                    max_x = len(self.selectors) * self.game.SIZE_PER_TILE
                    if (
                        y <= absolute_mouse_pos[1] < y + self.game.SIZE_PER_TILE
                        and absolute_mouse_pos[0] < max_x
                    ):
                        index = absolute_mouse_pos[0] // self.game.SIZE_PER_TILE
                        if index < len(self.selectors):
                            self.selected_obj = self.selectors[index]
                        continue

                if self.mode == 1:
                    if self.selected_obj is None:
                        continue
                    skip = False
                    if grid_position in self.game.position_map:
                        for x in self.game.position_map[grid_position]:
                            if not isinstance(x, Item):
                                skip = True
                                break
                    if skip:
                        continue
                    if self.selected_obj.cost > self.game.cash:
                        continue
                    if isinstance(self.selected_obj, Machine):
                        if isinstance(self.selected_obj, Seller) or isinstance(
                            self.selected_obj, Miner
                        ):
                            obj = self.selected_obj.__class__(self.game, mouse_pos)
                        else:
                            obj = self.selected_obj.__class__(
                                self.game, self.selected_obj.machine_id, mouse_pos
                            )
                    else:
                        obj = self.selected_obj.__class__(self.game, mouse_pos)
                    obj.direction = self.direction
                    obj.snap_to_grid()
                    obj.add_to_game()
                    if isinstance(obj, Machine):
                        obj.check_for_item()
                    self.game.remove_cash(self.selected_obj.cost)
                    self.game.statistics.increment("items_spawned")
                elif self.mode == 2:
                    if grid_position not in self.game.position_map:
                        self.start_pos = pygame.mouse.get_pos()
                        self.cam_start_pos = self.game.camera.position
                    else:
                        self.obj_start_pos = self.game.position_map[grid_position]
                elif self.mode == 3:
                    if grid_position not in self.game.position_map:
                        continue

                    for x in self.game.position_map[grid_position]:
                        if isinstance(x, Item):
                            break

                        self.game.add_cash(x.cost / 2)
                        x.remove_from_game()

                        break

        if self.start_pos and self.mode == 2:
            mouse_pos = pygame.mouse.get_pos()
            moved = (mouse_pos[0] - self.start_pos[0], mouse_pos[1] - self.start_pos[1])
            self.game.camera.position = (
                self.cam_start_pos[0] - moved[0],
                self.cam_start_pos[1] - moved[1],
            )
