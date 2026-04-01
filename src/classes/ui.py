from __future__ import annotations


from src.static_config import GRID_SIZE, SPRITE_LAYER
from src.constants import (
    COLOR_GRID_FILL,
    COLOR_GRID_MAIN_AXIS,
    COLOR_GRID_SECONDARY_AXIS,
    COLOR_ICON_ERROR_BG,
    COLOR_ICON_ERROR_BORDER,
    COLOR_ICON_ERROR_TEXT,
    COLOR_PLACEMENT_VALID,
    COLOR_PLACEMENT_INVALID,
    COLOR_PLACEMENT_BORDER,
    COLOR_ZOOM_PANEL_BG,
    COLOR_ZOOM_PANEL_BORDER,
    COLOR_ZOOM_TEXT,
    COLOR_INFO_PANEL_BG,
    COLOR_INFO_PANEL_BORDER,
    COLOR_INFO_PANEL_TEXT,
    COLOR_DEBUG_VISIBLE,
    COLOR_DEBUG_INVISIBLE,
    COLOR_DEBUG_BELT_LINK,
    COLOR_RECIPE_OVERLAY,
    COLOR_RECIPE_TITLE,
    COLOR_RECIPE_LEFT_PANEL_BG,
    COLOR_RECIPE_LEFT_PANEL_BORDER,
    COLOR_RECIPE_ROW_SELECTED_BG,
    COLOR_RECIPE_ROW_UNSELECTED_BG,
    COLOR_RECIPE_ROW_SELECTED_BORDER,
    COLOR_RECIPE_LABEL_TEXT,
    COLOR_RECIPE_COST_TEXT,
    COLOR_RECIPE_RIGHT_PANEL_BG,
    COLOR_RECIPE_RIGHT_PANEL_BORDER,
    COLOR_RECIPE_MACHINE_TITLE,
    COLOR_RECIPE_DESCRIPTION,
    COLOR_RECIPE_NO_RECIPES,
    COLOR_RECIPE_CARD_BG,
    COLOR_RECIPE_CARD_BORDER,
    COLOR_RECIPE_DURATION,
    COLOR_RECIPE_INPUT_AMOUNT,
    COLOR_RECIPE_INPUT_NAME,
    COLOR_RECIPE_ARROW,
    COLOR_RECIPE_OUTPUT_AMOUNT,
    COLOR_RECIPE_OUTPUT_NAME,
    COLOR_MODE_PANEL_BG,
    COLOR_MODE_PANEL_BORDER,
    COLOR_MODE_TEXT,
    COLOR_CASH_TEXT,
    COLOR_HINT_TEXT,
    COLOR_SELECTOR_SELECTED_BORDER,
    COLOR_SELECTOR_UNSELECTED_BORDER,
    COLOR_MACHINE_RECIPE_MENU_BG,
    COLOR_MACHINE_RECIPE_MENU_BORDER,
    COLOR_MACHINE_RECIPE_MENU_ROW,
    COLOR_MACHINE_RECIPE_MENU_ROW_SELECTED,
    COLOR_MACHINE_RECIPE_MENU_ROW_HOVER,
    COLOR_MACHINE_RECIPE_MENU_TEXT,
    COLOR_MACHINE_RECIPE_MENU_TEXT_SELECTED,
    FONT_MAIN_SIZE,
    FONT_ICON_SIZE,
    FONT_MEDIUM_SIZE,
    UI_ZOOM_PANEL_WIDTH,
    UI_ZOOM_PANEL_HEIGHT,
    UI_EDGE_PADDING_X,
    UI_EDGE_PADDING_Y,
    UI_PANEL_PADDING_X,
    UI_PANEL_PADDING_Y,
    UI_INFO_PANEL_MAX_WIDTH,
    UI_INFO_PANEL_X_PADDING,
    UI_INFO_PANEL_Y_OFFSET,
    UI_INFO_PANEL_LINE_HEIGHT,
    UI_INFO_PANEL_PADDING,
    UI_INFO_PANEL_Y_PADDING,
    UI_MODE_PANEL_X,
    UI_MODE_PANEL_Y,
    UI_MODE_PANEL_WIDTH,
    UI_MODE_PANEL_HEIGHT,
    UI_RECIPE_BOOK_LEFT_X,
    UI_RECIPE_BOOK_LEFT_Y,
    UI_RECIPE_BOOK_LEFT_W,
    UI_RECIPE_BOOK_ITEM_H,
    UI_RECIPE_BOOK_LEFT_PADDING,
    UI_RECIPE_BOOK_LEFT_MARGIN,
    UI_RECIPE_BOOK_RIGHT_LEFT_MARGIN,
    UI_RECIPE_CARD_HEIGHT,
    UI_RECIPE_CARD_ICON_SIZE,
    UI_RECIPE_CARD_ICON_Y,
    UI_RECIPE_CARD_AMOUNT_Y,
    UI_RECIPE_CARD_NAME_Y,
    UI_RECIPE_CARD_DURATION_COL_WIDTH,
    UI_SELECTOR_ICON_MARGIN,
    UI_MACHINE_RECIPE_MENU_WIDTH,
    UI_MACHINE_RECIPE_MENU_PADDING,
    UI_MACHINE_RECIPE_MENU_ROW_HEIGHT,
    UI_TEXT_RECIPE_BOOK_TITLE,
    UI_TEXT_MINER_DESCRIPTION,
    UI_TEXT_SELLER_DESCRIPTION,
    UI_TEXT_NO_RECIPES,
    UI_TEXT_HINT,
)
from src.classes import EventEmitter, ImageCache
from pygame.sprite import DirtySprite
from src.objects import Machine, Belt
from typing import TYPE_CHECKING
from pygame import (
    SRCALPHA,
    Rect,
    Surface,
    Vector2,
    display,
    draw,
    freetype,
    mouse,
    transform,
)

if TYPE_CHECKING:
    from src.classes.input import SelectorOption
    from src.game import Game


class GridSprite(DirtySprite):
    def __init__(self, game: Game):
        super().__init__()

        self.game = game

        self.image: Surface = Surface(
            display.get_window_size(), SRCALPHA
        ).convert_alpha()
        self.rect: Rect = self.image.get_rect(topleft=(0, 0))
        self.dirty = 1
        self.visible = 1

        self.game.camera.on("move", self._redraw)
        self.game.camera.on("resize", self._on_resize)
        self.game.camera.on("zoom", self._redraw)
        self._redraw()

    def _on_resize(self):
        self.image = Surface(display.get_window_size(), SRCALPHA).convert_alpha()
        self.rect = self.image.get_rect(topleft=(0, 0))
        self._redraw()

    def _redraw(self):
        assert self.image is not None
        assert self.rect is not None

        width = self.rect.width
        height = self.rect.height

        self.image.fill(COLOR_GRID_FILL)

        zoom = self.game.camera.zoom
        cam_x = self.game.camera.position.x
        cam_y = self.game.camera.position.y

        first_world_x = int(cam_x // GRID_SIZE) * GRID_SIZE
        last_world_x = cam_x + (width / zoom) + GRID_SIZE
        world_x = first_world_x
        while world_x <= last_world_x:
            screen_x = int((world_x - cam_x) * zoom)
            color = COLOR_GRID_MAIN_AXIS if world_x == 0 else COLOR_GRID_SECONDARY_AXIS
            draw.line(self.image, color, (screen_x, 0), (screen_x, height), 1)
            world_x += GRID_SIZE

        first_world_y = int(cam_y // GRID_SIZE) * GRID_SIZE
        last_world_y = cam_y + (height / zoom) + GRID_SIZE
        world_y = first_world_y
        while world_y <= last_world_y:
            screen_y = int((world_y - cam_y) * zoom)
            color = COLOR_GRID_MAIN_AXIS if world_y == 0 else COLOR_GRID_SECONDARY_AXIS
            draw.line(self.image, color, (0, screen_y), (width, screen_y), 1)
            world_y += GRID_SIZE

        self.dirty = 1

    def destroy(self):
        self.game.camera.remove_listener("move", self._redraw)
        self.game.camera.remove_listener("resize", self._on_resize)
        self.game.camera.remove_listener("zoom", self._redraw)


class UI(EventEmitter, DirtySprite):
    def __init__(self, game: Game):
        EventEmitter.__init__(self)
        DirtySprite.__init__(self)

        self.game = game
        self.grid_sprite = GridSprite(game)
        self.image: Surface = Surface(
            display.get_window_size(), SRCALPHA
        ).convert_alpha()
        self.rect: Rect = self.image.get_rect(topleft=(0, 0))
        self.dirty = 1
        self.visible = 1
        if not freetype.get_init():
            freetype.init()
        self._font = freetype.SysFont("Arial", FONT_MAIN_SIZE, bold=True)
        self._icon_font = freetype.SysFont("Arial", FONT_ICON_SIZE, bold=True)
        self._medium_font = freetype.SysFont("Arial", FONT_MEDIUM_SIZE, bold=False)
        self._icon_cache: dict[str, Surface] = {}

        self.game.camera.on("resize", self._on_resize)
        self.game.on("update", self._on_update)
        self._redraw()

        self.game.sprite_layers.add(self.grid_sprite, layer=SPRITE_LAYER.GRID)
        self.game.sprite_layers.add(self, layer=SPRITE_LAYER.UI)

    def __del__(self):
        self.destroy()

    def _on_resize(self):
        self.image = Surface(display.get_window_size(), SRCALPHA).convert_alpha()
        self.rect = self.image.get_rect(topleft=(0, 0))
        self._redraw()

    def _on_update(self, _: float):
        self._redraw()

    def _selector_sprite_path(self, option: SelectorOption) -> str:
        if option.kind == "belt":
            return "assets/sprite/belt.png"

        if option.kind in ["seller", "miner"]:
            return self.game.data.get_machine_data(option.kind)["sprite"]

        if option.kind == "machine" and option.machine_type is not None:
            return self.game.data.get_machine_data(option.machine_type)["sprite"]

        return "assets/sprite/unknown.png"

    def _placeholder_icon(self, path: str, size: tuple[int, int]) -> Surface:
        icon = Surface(size, SRCALPHA).convert_alpha()
        icon.fill(COLOR_ICON_ERROR_BG)
        draw.rect(icon, COLOR_ICON_ERROR_BORDER, icon.get_rect(), width=2)

        text = path.split("/")[-1]
        label, _ = self._icon_font.render(text, COLOR_ICON_ERROR_TEXT)
        label_rect = label.get_rect(center=(size[0] // 2, size[1] // 2))
        icon.blit(label, label_rect)
        return icon

    def _get_selector_icon(
        self, option: SelectorOption, size: tuple[int, int]
    ) -> Surface:
        path = self._selector_sprite_path(option)
        cache_key = f"{path}:{size[0]}x{size[1]}"
        if cache_key in self._icon_cache:
            return self._icon_cache[cache_key]

        loaded = ImageCache.get(path)
        if loaded is not None:
            icon = transform.scale(loaded, size)
        else:
            icon = self._placeholder_icon(path, size)

        self._icon_cache[cache_key] = icon
        return icon

    def _can_place_selected(
        self, selected: SelectorOption | None, grid_pos: tuple[int, int]
    ) -> bool:
        if selected is None:
            return False

        if selected.cost > self.game.data.cash:
            return False

        if grid_pos in self.game.position_map:
            for obj in self.game.position_map[grid_pos]:
                from src.objects.item import Item

                if not isinstance(obj, Item):
                    return False

        return True

    def _draw_cursor_preview(self, selected: SelectorOption | None, mode: int):
        if mode != 1 or selected is None:
            return

        mouse_pos = Vector2(mouse.get_pos())
        world_pos = self.game.camera.screen_to_world(mouse_pos)
        grid_pos = (int(world_pos.x // GRID_SIZE), int(world_pos.y // GRID_SIZE))

        world_tile = Vector2(grid_pos[0] * GRID_SIZE, grid_pos[1] * GRID_SIZE)
        screen_tile = self.game.camera.world_to_screen(world_tile)
        tile_size = max(1, int(GRID_SIZE * self.game.camera.zoom))
        tile_rect = Rect(int(screen_tile.x), int(screen_tile.y), tile_size, tile_size)

        can_place = self._can_place_selected(selected, grid_pos)
        tile_color = COLOR_PLACEMENT_VALID if can_place else COLOR_PLACEMENT_INVALID
        draw.rect(self.image, tile_color, tile_rect)
        draw.rect(self.image, COLOR_PLACEMENT_BORDER, tile_rect, width=2)

        icon_side = max(1, tile_size - 8)
        icon_size = (icon_side, icon_side)
        base_icon = self._get_selector_icon(selected, icon_size)
        rotated_icon = transform.rotate(base_icon, self.game.input.placement_rotation)
        rotated_icon.set_alpha(180 if can_place else 130)

        icon_rect = rotated_icon.get_rect(center=tile_rect.center)
        self.image.blit(rotated_icon, icon_rect)

    def _get_hovered_machine(self) -> Machine | None:
        mouse_pos = Vector2(mouse.get_pos())
        world_pos = self.game.camera.screen_to_world(mouse_pos)
        grid_pos = (int(world_pos.x // GRID_SIZE), int(world_pos.y // GRID_SIZE))

        if grid_pos not in self.game.position_map:
            return None

        for obj in self.game.position_map[grid_pos]:
            if isinstance(obj, Machine) and not obj.destroyed:
                return obj

        return None

    def _draw_zoom_info(self):
        zoom_panel = Rect(
            self.rect.width - UI_ZOOM_PANEL_WIDTH - UI_EDGE_PADDING_X,
            UI_EDGE_PADDING_Y,
            UI_ZOOM_PANEL_WIDTH,
            UI_ZOOM_PANEL_HEIGHT,
        )
        draw.rect(self.image, COLOR_ZOOM_PANEL_BG, zoom_panel, border_radius=6)
        draw.rect(
            self.image, COLOR_ZOOM_PANEL_BORDER, zoom_panel, width=2, border_radius=6
        )

        zoom_text, _ = self._font.render(
            f"Zoom: {self.game.camera.zoom:.2f}x", COLOR_ZOOM_TEXT
        )
        text_rect = zoom_text.get_rect(center=zoom_panel.center)
        self.image.blit(zoom_text, text_rect)

    def _draw_hovered_machine_info(self):
        from src.machines.miner import Miner
        from src.machines.seller import Seller

        machine = self._get_hovered_machine()
        if machine is None:
            return

        lines = [f"Position: {machine.position}"]

        if isinstance(machine, Miner):
            lines.append("Machine type: Miner")
            lines.append(f"Ore type: {machine.ore_type}")
            lines.append(f"Timer: {machine.timer}")
        elif isinstance(machine, Seller):
            lines.append("Machine type: Seller")
        else:
            lines.append(f"Machine type: {machine.type}")
            lines.append(f"Timer: {machine.timer}")
            selected_recipe = machine.get_selected_recipe()
            if selected_recipe is None:
                lines.append("Recipe mode: Auto")
            else:
                recipe = machine.recipes[selected_recipe]
                outputs = ", ".join(
                    out["type"].replace("_", " ") for out in recipe["outputs"]
                )
                lines.append(f"Recipe mode: {selected_recipe + 1} ({outputs})")
            lines.append(f"Inventory: {machine.inventory}")

        panel_width = min(UI_INFO_PANEL_MAX_WIDTH, self.rect.width - 24)
        panel_x = self.rect.width - panel_width - UI_INFO_PANEL_X_PADDING
        panel_y = UI_INFO_PANEL_Y_OFFSET
        line_height = UI_INFO_PANEL_LINE_HEIGHT
        panel_height = (
            UI_INFO_PANEL_PADDING + (line_height * len(lines)) + UI_INFO_PANEL_Y_PADDING
        )
        info_panel = Rect(panel_x, panel_y, panel_width, panel_height)
        draw.rect(self.image, COLOR_INFO_PANEL_BG, info_panel, border_radius=6)
        draw.rect(
            self.image, COLOR_INFO_PANEL_BORDER, info_panel, width=2, border_radius=6
        )

        y = info_panel.y + UI_INFO_PANEL_PADDING
        for line in lines:
            text_surf, _ = self._icon_font.render(line, COLOR_INFO_PANEL_TEXT)
            self.image.blit(text_surf, (info_panel.x + UI_INFO_PANEL_PADDING, y))
            y += line_height

    def _draw_debug_rects(self):

        for x in self.game.objects:
            debug_rect = x.screen_rect.copy()
            draw.rect(
                self.image,
                COLOR_DEBUG_VISIBLE if x.visible else COLOR_DEBUG_INVISIBLE,
                debug_rect,
                width=1,
            )

    def _draw_debug_belt_links(self):
        drawn_links: set[tuple[int, int]] = set()
        for x in self.game.objects:
            if not isinstance(x, Belt):
                continue

            neighbors: list[Belt] = [x.next] if x.next else []
            neighbors.extend(x.prevs)

            for neighbor in neighbors:
                x_id = id(x)
                neighbor_id = id(neighbor)
                link_key = (
                    (x_id, neighbor_id) if x_id <= neighbor_id else (neighbor_id, x_id)
                )
                if link_key in drawn_links:
                    continue
                drawn_links.add(link_key)

                a = self.game.camera.world_to_screen(x.position)
                b = self.game.camera.world_to_screen(neighbor.position)
                half_grid = (GRID_SIZE * self.game.camera.zoom) / 2

                a_line = (
                    a.x + half_grid,
                    a.y + half_grid,
                )
                b_line = (
                    b.x + half_grid,
                    b.y + half_grid,
                )

                draw.line(
                    self.image,
                    COLOR_DEBUG_BELT_LINK,
                    a_line,
                    b_line,
                    width=1,
                )

    def _get_item_icon(self, sprite_path: str, size: tuple[int, int]) -> Surface:
        cache_key = f"{sprite_path}:{size[0]}x{size[1]}"
        if cache_key in self._icon_cache:
            return self._icon_cache[cache_key]
        loaded = ImageCache.get(sprite_path)
        if loaded is not None:
            icon = transform.scale(loaded, size)
        else:
            icon = self._placeholder_icon(sprite_path, size)
        self._icon_cache[cache_key] = icon
        return icon

    def _draw_recipe_book(self):
        from src.classes.data import Data

        screen_w, screen_h = self.rect.width, self.rect.height

        overlay = Surface((screen_w, screen_h), SRCALPHA)
        overlay.fill(COLOR_RECIPE_OVERLAY)
        self.image.blit(overlay, (0, 0))

        title_surf, _ = self._font.render(UI_TEXT_RECIPE_BOOK_TITLE, COLOR_RECIPE_TITLE)
        self.image.blit(title_surf, (screen_w // 2 - title_surf.get_width() // 2, 10))

        machines = [k for k in Data.machine_data.keys() if k != "unknown"]

        LEFT_X, LEFT_Y, LEFT_W, ITEM_H = (
            UI_RECIPE_BOOK_LEFT_X,
            UI_RECIPE_BOOK_LEFT_Y,
            UI_RECIPE_BOOK_LEFT_W,
            UI_RECIPE_BOOK_ITEM_H,
        )
        left_panel = Rect(
            LEFT_X, LEFT_Y, LEFT_W, screen_h - LEFT_Y - UI_RECIPE_BOOK_LEFT_MARGIN
        )
        draw.rect(self.image, COLOR_RECIPE_LEFT_PANEL_BG, left_panel, border_radius=8)
        draw.rect(
            self.image,
            COLOR_RECIPE_LEFT_PANEL_BORDER,
            left_panel,
            width=1,
            border_radius=8,
        )

        scroll = self.game.input.recipe_book_scroll
        selected_idx = self.game.input.recipe_book_machine_idx
        y = LEFT_Y + UI_RECIPE_BOOK_LEFT_PADDING
        for i, machine_type in enumerate(machines):
            if i < scroll:
                continue
            if y + ITEM_H > left_panel.bottom - UI_RECIPE_BOOK_LEFT_PADDING:
                break
            row = Rect(LEFT_X + 4, y, LEFT_W - 8, ITEM_H - 3)
            is_sel = i == selected_idx
            draw.rect(
                self.image,
                COLOR_RECIPE_ROW_SELECTED_BG
                if is_sel
                else COLOR_RECIPE_ROW_UNSELECTED_BG,
                row,
                border_radius=4,
            )
            if is_sel:
                draw.rect(
                    self.image,
                    COLOR_RECIPE_ROW_SELECTED_BORDER,
                    row,
                    width=1,
                    border_radius=4,
                )

            sprite_path = Data.machine_data[machine_type]["sprite"]
            icon = self._get_item_icon(sprite_path, (28, 28))
            self.image.blit(icon, (row.x + 4, row.y + 6))

            label = machine_type.replace("_", " ").title()
            lbl_surf, _ = self._medium_font.render(label, COLOR_RECIPE_LABEL_TEXT)
            self.image.blit(lbl_surf, (row.x + 36, row.y + 4))
            cost = Data.machine_data[machine_type]["cost"]
            cost_surf, _ = self._icon_font.render(f"${cost:,}", COLOR_RECIPE_COST_TEXT)
            self.image.blit(cost_surf, (row.x + 36, row.y + 22))
            y += ITEM_H

        RIGHT_X = LEFT_X + LEFT_W + UI_RECIPE_BOOK_RIGHT_LEFT_MARGIN
        right_panel = Rect(
            RIGHT_X,
            LEFT_Y,
            screen_w - RIGHT_X - UI_EDGE_PADDING_X,
            screen_h - LEFT_Y - UI_EDGE_PADDING_Y,
        )
        draw.rect(self.image, COLOR_RECIPE_RIGHT_PANEL_BG, right_panel, border_radius=8)
        draw.rect(
            self.image,
            COLOR_RECIPE_RIGHT_PANEL_BORDER,
            right_panel,
            width=1,
            border_radius=8,
        )

        if selected_idx >= len(machines):
            return
        machine_type = machines[selected_idx]
        machine_data = Data.machine_data[machine_type]
        recipes = machine_data["recipes"]

        title2, _ = self._font.render(
            machine_type.replace("_", " ").title(), COLOR_RECIPE_MACHINE_TITLE
        )
        self.image.blit(title2, (right_panel.x + 12, right_panel.y + 8))

        desc_y = right_panel.y + 36
        if machine_type == "miner":
            desc, _ = self._medium_font.render(
                UI_TEXT_MINER_DESCRIPTION, COLOR_RECIPE_DESCRIPTION
            )
            self.image.blit(desc, (right_panel.x + 12, desc_y))
            return
        if machine_type == "seller":
            desc, _ = self._medium_font.render(
                UI_TEXT_SELLER_DESCRIPTION, COLOR_RECIPE_DESCRIPTION
            )
            self.image.blit(desc, (right_panel.x + 12, desc_y))
            return
        if not recipes:
            desc, _ = self._medium_font.render(
                UI_TEXT_NO_RECIPES, COLOR_RECIPE_NO_RECIPES
            )
            self.image.blit(desc, (right_panel.x + 12, desc_y))
            return

        RECIPE_H = UI_RECIPE_CARD_HEIGHT
        ICON_SIZE = UI_RECIPE_CARD_ICON_SIZE
        ICON_Y = UI_RECIPE_CARD_ICON_Y
        AMOUNT_Y = UI_RECIPE_CARD_AMOUNT_Y
        NAME_Y = UI_RECIPE_CARD_NAME_Y
        CARD_H = RECIPE_H - 4
        DUR_COL_W = UI_RECIPE_CARD_DURATION_COL_WIDTH

        ry = desc_y
        for recipe in recipes:
            if ry + RECIPE_H > right_panel.bottom - UI_PANEL_PADDING_Y:
                break
            card = Rect(
                right_panel.x + UI_PANEL_PADDING_X,
                ry,
                right_panel.width - (UI_PANEL_PADDING_X * 2),
                CARD_H,
            )
            draw.rect(self.image, COLOR_RECIPE_CARD_BG, card, border_radius=5)
            draw.rect(
                self.image, COLOR_RECIPE_CARD_BORDER, card, width=1, border_radius=5
            )

            dur_surf, _ = self._medium_font.render(
                f"{recipe['duration']}s", COLOR_RECIPE_DURATION
            )
            dur_y = card.y + (CARD_H - dur_surf.get_height()) // 2
            self.image.blit(dur_surf, (card.x + 6, dur_y))

            rx = card.x + DUR_COL_W

            for inp in recipe["inputs"]:
                item_d = Data.get_item_data(inp["type"])
                icon = self._get_item_icon(item_d["sprite"], (ICON_SIZE, ICON_SIZE))
                self.image.blit(icon, (rx, card.y + ICON_Y))
                amount_surf, _ = self._icon_font.render(
                    f"×{inp['amount']}", COLOR_RECIPE_INPUT_AMOUNT
                )
                self.image.blit(amount_surf, (rx, card.y + AMOUNT_Y))
                name_surf, _ = self._icon_font.render(
                    inp["type"].replace("_", " "), COLOR_RECIPE_INPUT_NAME
                )
                self.image.blit(name_surf, (rx, card.y + NAME_Y))
                col_w = max(ICON_SIZE + 6, name_surf.get_width() + 6)
                rx += col_w + 4

            arrow_surf, _ = self._font.render("→", COLOR_RECIPE_ARROW)
            arrow_y = card.y + (CARD_H - arrow_surf.get_height()) // 2
            self.image.blit(arrow_surf, (rx, arrow_y))
            rx += arrow_surf.get_width() + 8

            for out in recipe["outputs"]:
                item_d = Data.get_item_data(out["type"])
                price = item_d.get("price", 0)
                icon = self._get_item_icon(item_d["sprite"], (ICON_SIZE, ICON_SIZE))
                self.image.blit(icon, (rx, card.y + ICON_Y))
                amount_surf, _ = self._icon_font.render(
                    f"×{out['amount']}", COLOR_RECIPE_OUTPUT_AMOUNT
                )
                self.image.blit(amount_surf, (rx, card.y + AMOUNT_Y))
                name_surf, _ = self._icon_font.render(
                    f"{out['type'].replace('_', ' ')}  ${price:,}",
                    COLOR_RECIPE_OUTPUT_NAME,
                )
                self.image.blit(name_surf, (rx, card.y + NAME_Y))
                col_w = max(ICON_SIZE + 6, name_surf.get_width() + 6)
                rx += col_w + 4

            ry += RECIPE_H

    def _draw_machine_recipe_menu(self):
        input_state = self.game.input
        machine = input_state.machine_recipe_menu_machine
        if not input_state.machine_recipe_menu_open or machine is None:
            return

        option_count = len(machine.recipes) + 1
        menu_w = min(
            UI_MACHINE_RECIPE_MENU_WIDTH,
            max(120, self.rect.width - (UI_EDGE_PADDING_X * 2)),
        )
        menu_h = (UI_MACHINE_RECIPE_MENU_PADDING * 2) + (
            UI_MACHINE_RECIPE_MENU_ROW_HEIGHT * option_count
        )
        menu_h = min(menu_h, max(60, self.rect.height - (UI_EDGE_PADDING_Y * 2)))
        screen_w, screen_h = self.rect.width, self.rect.height

        menu_x = int(input_state.machine_recipe_menu_pos.x)
        menu_y = int(input_state.machine_recipe_menu_pos.y)
        menu_x = min(
            max(UI_EDGE_PADDING_X, menu_x),
            max(UI_EDGE_PADDING_X, screen_w - menu_w - UI_EDGE_PADDING_X),
        )
        menu_y = min(
            max(UI_EDGE_PADDING_Y, menu_y),
            max(UI_EDGE_PADDING_Y, screen_h - menu_h - UI_EDGE_PADDING_Y),
        )

        panel = Rect(menu_x, menu_y, menu_w, menu_h)
        draw.rect(self.image, COLOR_MACHINE_RECIPE_MENU_BG, panel, border_radius=8)
        draw.rect(
            self.image,
            COLOR_MACHINE_RECIPE_MENU_BORDER,
            panel,
            width=2,
            border_radius=8,
        )

        selected_recipe = machine.get_selected_recipe()
        mouse_pos = Vector2(mouse.get_pos())
        base_y = panel.y + UI_MACHINE_RECIPE_MENU_PADDING
        for row_idx in range(option_count):
            row_rect = Rect(
                panel.x + UI_PANEL_PADDING_X,
                base_y + (row_idx * UI_MACHINE_RECIPE_MENU_ROW_HEIGHT),
                panel.width - (UI_PANEL_PADDING_X * 2),
                UI_MACHINE_RECIPE_MENU_ROW_HEIGHT - 2,
            )

            is_selected = row_idx == 0 if selected_recipe is None else row_idx == (selected_recipe + 1)
            is_hovered = row_rect.collidepoint(mouse_pos.x, mouse_pos.y)

            row_color = COLOR_MACHINE_RECIPE_MENU_ROW
            if is_selected:
                row_color = COLOR_MACHINE_RECIPE_MENU_ROW_SELECTED
            elif is_hovered:
                row_color = COLOR_MACHINE_RECIPE_MENU_ROW_HOVER
            draw.rect(self.image, row_color, row_rect, border_radius=5)

            icon_size = max(16, UI_MACHINE_RECIPE_MENU_ROW_HEIGHT - 10)
            icon_x = row_rect.x + UI_PANEL_PADDING_Y
            icon_y = row_rect.y + (row_rect.height - icon_size) // 2
            text_x = icon_x + icon_size + UI_PANEL_PADDING_Y

            if row_idx == 0:
                label = "Auto (first available recipe)"
                machine_data = self.game.data.get_machine_data(machine.type)
                icon = self._get_item_icon(
                    machine_data["sprite"], (icon_size, icon_size)
                )
            else:
                recipe = machine.recipes[row_idx - 1]
                inputs = " + ".join(
                    f"{inp['amount']}x {inp['type'].replace('_', ' ')}"
                    for inp in recipe["inputs"]
                )
                outputs = " + ".join(
                    f"{out['amount']}x {out['type'].replace('_', ' ')}"
                    for out in recipe["outputs"]
                )
                if inputs == "":
                    inputs = "none"
                if outputs == "":
                    outputs = "none"
                label = f"{row_idx}. {inputs} -> {outputs} ({recipe['duration']}s)"
                first_output = recipe["outputs"][0] if recipe["outputs"] else None
                if first_output is not None:
                    item_data = self.game.data.get_item_data(first_output["type"])
                    icon = self._get_item_icon(
                        item_data["sprite"], (icon_size, icon_size)
                    )
                else:
                    machine_data = self.game.data.get_machine_data(machine.type)
                    icon = self._get_item_icon(
                        machine_data["sprite"], (icon_size, icon_size)
                    )

            text_color = (
                COLOR_MACHINE_RECIPE_MENU_TEXT_SELECTED
                if is_selected
                else COLOR_MACHINE_RECIPE_MENU_TEXT
            )
            self.image.blit(icon, (icon_x, icon_y))
            label_surf, _ = self._medium_font.render(label, text_color)
            self.image.blit(label_surf, (text_x, row_rect.y + UI_PANEL_PADDING_Y // 2))

    def _redraw(self):
        assert self.image is not None
        assert self.rect is not None

        self.image.fill(COLOR_GRID_FILL)

        selectors = self.game.input.selectors
        selected = self.game.input.selected_obj
        mode = self.game.input.mode

        mode_names = {
            1: "PLACE",
            2: "MOVE",
            3: "REMOVE",
        }

        mode_text, _ = self._font.render(
            f"Mode: {mode_names.get(mode, 'UNKNOWN')}", COLOR_MODE_TEXT
        )
        cash_text, _ = self._font.render(
            f"Cash: ${int(self.game.data.cash):,}", COLOR_CASH_TEXT
        )
        hint_text, _ = self._medium_font.render(UI_TEXT_HINT, COLOR_HINT_TEXT)

        line_gap = 4
        content_width = max(
            mode_text.get_width(),
            cash_text.get_width(),
            hint_text.get_width(),
        )
        content_height = (
            mode_text.get_height()
            + cash_text.get_height()
            + hint_text.get_height()
            + (line_gap * 2)
        )

        panel_width = max(UI_MODE_PANEL_WIDTH, content_width + (UI_PANEL_PADDING_X * 2))
        panel_height = max(
            UI_MODE_PANEL_HEIGHT,
            content_height + (UI_PANEL_PADDING_Y * 2),
        )

        panel_width = min(panel_width, self.rect.width - (UI_EDGE_PADDING_X * 2))
        panel_height = min(panel_height, self.rect.height - (UI_EDGE_PADDING_Y * 2))

        mode_panel = Rect(
            UI_MODE_PANEL_X,
            UI_MODE_PANEL_Y,
            panel_width,
            panel_height,
        )
        draw.rect(self.image, COLOR_MODE_PANEL_BG, mode_panel, border_radius=6)
        draw.rect(
            self.image, COLOR_MODE_PANEL_BORDER, mode_panel, width=2, border_radius=6
        )

        text_x = mode_panel.x + UI_PANEL_PADDING_X
        text_y = mode_panel.y + UI_PANEL_PADDING_Y
        self.image.blit(mode_text, (text_x, text_y))
        text_y += mode_text.get_height() + line_gap
        self.image.blit(cash_text, (text_x, text_y))
        text_y += cash_text.get_height() + line_gap
        self.image.blit(hint_text, (text_x, text_y))

        y = self.rect.height - UI_EDGE_PADDING_Y - GRID_SIZE
        x = UI_EDGE_PADDING_X

        for option in selectors:
            slot = Rect(x, y, GRID_SIZE, GRID_SIZE)

            bg = (35, 35, 35, 220) if mode == 1 else (20, 20, 20, 170)
            border = (
                COLOR_SELECTOR_SELECTED_BORDER
                if option is selected and mode == 1
                else COLOR_SELECTOR_UNSELECTED_BORDER
            )
            draw.rect(self.image, bg, slot)
            draw.rect(self.image, border, slot, width=2)

            icon_rect = slot.inflate(-UI_SELECTOR_ICON_MARGIN, -UI_SELECTOR_ICON_MARGIN)
            icon = self._get_selector_icon(option, (icon_rect.width, icon_rect.height))
            self.image.blit(icon, icon_rect)
            x += GRID_SIZE

        self._draw_cursor_preview(selected, mode)
        self._draw_zoom_info()
        self._draw_hovered_machine_info()
        self._draw_machine_recipe_menu()

        if self.game.input.recipe_book_open:
            self._draw_recipe_book()

        if self.game.DEBUG:
            self._draw_debug_rects()
            self._draw_debug_belt_links()

        self.dirty = 1

    def destroy(self):
        self.grid_sprite.destroy()
        self.game.sprite_layers.remove(self.grid_sprite)
        self.game.sprite_layers.remove(self)
        self.game.camera.remove_listener("resize", self._on_resize)
        self.game.remove_listener("update", self._on_update)
        self.remove_all_listeners()
        self._icon_cache.clear()
