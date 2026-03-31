from __future__ import annotations

from pygame import Rect, Surface, draw, freetype
from src.scenes.base import Scene
from typing import TYPE_CHECKING
import pygame


if TYPE_CHECKING:
    from src.game import Game


class GameScene(Scene):
    def __init__(self, game: Game):
        super().__init__(game, "game")
        self._loaded_slot: str | None = None
        self._menu_button_rect = Rect(14, 102, 150, 36)

        if not freetype.get_init():
            freetype.init()
        self._menu_button_font = freetype.SysFont("Arial", 18, bold=True)

    def enter(self):
        if not self.game.runtime_systems_ready:
            self.game.logger.warning(
                "Runtime systems were not ready when entering game scene, redirecting to loading"
            )
            self.game.scene_manager.change_scene("loading")
            return

        if self._loaded_slot != self.game.active_save_path:
            self.game.data.load(self.game.active_save_path)
            self._loaded_slot = self.game.active_save_path
        self.game.request_flip(rebuild_bg=True)

    def handle_event(self, evt: pygame.event.Event):
        if evt.type == pygame.MOUSEBUTTONDOWN and getattr(evt, "button", 0) == 1:
            if (
                not self.game.input.recipe_book_open
                and self._menu_button_rect.collidepoint(evt.pos)
            ):
                self.game.scene_manager.change_scene("main_menu")
                return

        if evt.type == pygame.KEYDOWN and evt.key == pygame.K_ESCAPE:
            self.game.scene_manager.change_scene("main_menu")
            return

        self.game.emit(f"PYGAME_{evt.type}", evt.dict)

    def update(self, dt: float):
        self.game.emit("update", dt)

    def render(self, surface: Surface):
        self.game.render_game_scene(surface, overlay_draw=self._draw_menu_button)

    def _draw_menu_button(self, surface: Surface):
        if self.game.input.recipe_book_open:
            return
        draw.rect(surface, (32, 36, 43), self._menu_button_rect, border_radius=8)
        draw.rect(
            surface,
            (140, 160, 180),
            self._menu_button_rect,
            width=2,
            border_radius=8,
        )
        button_text, _ = self._menu_button_font.render("Main Menu", (235, 235, 235))
        button_text_rect = button_text.get_rect(center=self._menu_button_rect.center)
        surface.blit(button_text, button_text_rect)
