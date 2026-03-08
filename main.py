from __future__ import annotations

from src.game import Game
import pygame


def check_pygame_ce():
    if getattr(pygame, "IS_CE", False):
        return

    pygame.quit()

    from tkinter import messagebox

    messagebox.showerror(
        title="Please use pygame-ce!",
        message="""This game uses pygame-ce instead of pygame because it's outdated, and broken, and it doesn't work on newer version of macOS (I don't know why)""",
    )

    raise SystemExit


def main():
    check_pygame_ce()
    Game().start()


if __name__ == "__main__":
    main()
