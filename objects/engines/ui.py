from objects.game_object import GameObject
import pygame


class UI(GameObject):
    def __init__(self, game):
        super().__init__(game)
        self.force_render = True
        self.x_sprite = pygame.image.load("assets/x.png")

    def __render_grid(self, screen):
        width, height = self.game.screen.get_size()
        tile_size = self.game.SIZE_PER_TILE
        camera = self.game.camera

        start_x = int(camera.position[0] // tile_size) * tile_size
        end_x = int(camera.position[0] + width)

        for x in range(start_x, end_x, tile_size):
            pygame.draw.line(
                screen,
                "White",
                camera.to_camera_position((x, camera.position[1])),
                camera.to_camera_position((x, camera.position[1] + height)),
            )

        start_y = int(camera.position[1] // tile_size) * tile_size
        end_y = int(camera.position[1] + height)

        for y in range(start_y, end_y, tile_size):
            pygame.draw.line(
                screen,
                "White",
                camera.to_camera_position((camera.position[0], y)),
                camera.to_camera_position((camera.position[0] + width, y)),
            )

    def __render_cursor(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.game.input.mode == 1 and self.game.input.selected_obj is not None:
            screen.blit(self.game.input.selected_obj.get_sprite(), mouse_pos)
        elif self.game.input.mode == 3:
            screen.blit(self.x_sprite, mouse_pos)

    def __render_selector(self, screen):
        if self.game.input.mode != 1:
            return

        width, height = pygame.display.get_window_size()
        y = height - 16 - self.game.SIZE_PER_TILE

        for x in range(width // self.game.SIZE_PER_TILE):
            if x < len(self.game.input.selectors):
                screen.blit(
                    self.game.FONTS["Arial"].render(
                        str(self.game.input.selectors[x].cost), True, "White"
                    ),
                    (x * self.game.SIZE_PER_TILE + 3, y - 20),
                )
                screen.blit(
                    self.game.input.selectors[x].get_sprite(),
                    (x * self.game.SIZE_PER_TILE, y),
                )

    def __render_ui(self, screen):
        mode = "Insert"

        if self.game.input.mode == 2:
            mode = "Move"
        elif self.game.input.mode == 3:
            mode = "Remove"

        screen.blit(
            self.game.FONTS["Arial"].render(f"Cash: {self.game.cash}", True, "White"),
            (0, 0),
        )
        screen.blit(
            self.game.FONTS["Arial"].render(f"Mode: {mode}", True, "White"), (0, 32)
        )

    def __render_debug(self, screen):
        mouse_grid_pos = (
            self.game.camera.to_world_position(pygame.mouse.get_pos())[0]
            // self.game.SIZE_PER_TILE,
            self.game.camera.to_world_position(pygame.mouse.get_pos())[1]
            // self.game.SIZE_PER_TILE,
        )

        elements = [
            self.game.FONTS["Arial"].render(
                f"Mouse Pos: {pygame.mouse.get_pos()}", True, "White"
            ),
            self.game.FONTS["Arial"].render(
                f"Pos: {self.game.camera.to_world_position(pygame.mouse.get_pos())}",
                True,
                "White",
            ),
            self.game.FONTS["Arial"].render(
                f"Grid Pos: {mouse_grid_pos}",
                True,
                "White",
            ),
            self.game.FONTS["Arial"].render(
                f"Obj count: {len(self.game.objects)}", True, "White"
            ),
        ]

        for x in range(len(elements)):
            screen.blit(
                elements[x],
                (0, (x * 18) + 64),
            )

    def render(self, screen):
        self.__render_grid(screen)
        self.__render_cursor(screen)
        self.__render_selector(screen)
        self.__render_ui(screen)

        if self.game.DEBUG:
            self.__render_debug(screen)
