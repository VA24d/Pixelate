"""Vacation Gallery - relaxing digital art on a 19x19 LED grid.

This is intentionally non-interactive "art viewing" for now.

Controls:
  - LEFT/RIGHT: switch between scenes (Beach / Waterfall)
  - SPACE: toggle gentle animation (on/off)
  - ESC: return to menu
"""

from __future__ import annotations

import math
import pygame

from games.base_game import Game, hsv_to_rgb
from games.sound import play_beep


class VacationGallery(Game):
    def __init__(self, grid):
        super().__init__(grid)
        self.scene_index = 0
        self.animate = True
        self.t = 0.0

        self.scenes = [
            {"name": "BEACH", "fn": self._render_beach},
            {"name": "FALLS", "fn": self._render_waterfall},
        ]

    def update(self, dt: float):
        if self.animate:
            self.t += dt

    def render(self):
        self.grid.clear((0, 0, 0))

        scene = self.scenes[self.scene_index]
        scene["fn"]()

        # Title
        self.grid.render_text("VACAY", 1, 0, (120, 200, 255), scale=1)
        self.grid.render_text(scene["name"], 1, 6, (255, 255, 0), scale=1)

        # Scene arrows
        arrow_color = (130, 130, 130)
        self._render_left_arrow(1, 10, arrow_color)
        self._render_right_arrow(17, 10, arrow_color)

    def handle_input(self, keys, events):
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                self.running = False
                return

            if event.key == pygame.K_LEFT:
                self.scene_index = (self.scene_index - 1) % len(self.scenes)
                play_beep(420, 35)
            elif event.key == pygame.K_RIGHT:
                self.scene_index = (self.scene_index + 1) % len(self.scenes)
                play_beep(520, 35)
            elif event.key == pygame.K_SPACE:
                self.animate = not self.animate
                play_beep(660, 50)

    # --- Scenes ---

    def _render_beach(self):
        """Sky + sun + ocean + sand, with optional wave shimmer."""
        # Sky
        for y in range(0, 6):
            for x in range(0, 19):
                c = (20, 60 + y * 10, 120 + y * 10)
                self.grid.set_pixel(x, y, c)

        # Sun
        sun_x, sun_y = 14, 2
        for dx, dy in [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]:
            self.grid.set_pixel(sun_x + dx, sun_y + dy, (255, 220, 80))

        # Ocean
        for y in range(6, 13):
            for x in range(0, 19):
                base = (0, 80 + (y - 6) * 8, 180)
                self.grid.set_pixel(x, y, base)

        # Waves shimmer
        if self.animate:
            phase = self.t * 3.0
            for x in range(0, 19):
                y = 8 + int(round((math.sin(phase + x * 0.6) + 1) * 0.8))
                self.grid.set_pixel(x, y, (120, 220, 255))

        # Sand
        for y in range(13, 19):
            for x in range(0, 19):
                self.grid.set_pixel(x, y, (180, 140, 70))

        # Palm silhouette
        for y in range(9, 16):
            self.grid.set_pixel(3, y, (40, 30, 20))
        for dx, dy in [(-2, 8), (-1, 8), (0, 8), (1, 8), (2, 8), (-1, 9), (1, 9)]:
            self.grid.set_pixel(3 + dx, dy, (20, 100, 40))

    def _render_waterfall(self):
        """Mountains + waterfall + pool with optional animated water."""
        # Sky
        for y in range(0, 6):
            for x in range(0, 19):
                self.grid.set_pixel(x, y, (10, 20 + y * 8, 60 + y * 12))

        # Mountains
        for x in range(0, 19):
            peak = 5 - int(abs(x - 6) * 0.6)
            for y in range(max(0, peak), 7):
                self.grid.set_pixel(x, y, (50, 60, 70))

        # Waterfall column
        fall_x = 10
        for y in range(4, 15):
            shade = 200 + (y % 2) * 30
            if self.animate:
                shade = 180 + int((math.sin(self.t * 6 + y) + 1) * 40)
            self.grid.set_pixel(fall_x, y, (80, shade, 255))
            self.grid.set_pixel(fall_x + 1, y, (60, shade - 20, 230))

        # Pool
        for y in range(15, 19):
            for x in range(0, 19):
                self.grid.set_pixel(x, y, (0, 80, 140))

        # Ripples
        if self.animate:
            for x in range(0, 19, 2):
                hue = (self.t * 80 + x * 15) % 360
                self.grid.set_pixel(x, 16 + (x % 3 == 0), hsv_to_rgb(hue, 0.4, 0.8))

        # Rocks
        for (x, y) in [(2, 17), (3, 18), (15, 17), (16, 18)]:
            self.grid.set_pixel(x, y, (70, 70, 70))

    def _render_left_arrow(self, x: int, y: int, color: tuple[int, int, int]):
        pts = [(0, 0), (1, -1), (1, 1), (2, -2), (2, 2)]
        for dx, dy in pts:
            self.grid.set_pixel(x + dx, y + dy, color)

    def _render_right_arrow(self, x: int, y: int, color: tuple[int, int, int]):
        pts = [(0, 0), (-1, -1), (-1, 1), (-2, -2), (-2, 2)]
        for dx, dy in pts:
            self.grid.set_pixel(x + dx, y + dy, color)
