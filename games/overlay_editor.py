"""Overlay editor: live pixel editing for menu logos + HUD sprites.

This is intentionally simple: you edit a single named sprite (w x h) that the
rest of the app can load via `games.sprite_store`.

Controls:
  - Arrow keys: move cursor
  - SPACE: paint selected color at cursor
  - BACKSPACE: erase pixel at cursor
  - C: cycle palette
  - S: save
  - ESC: exit editor

Mouse:
  - Left click paints at the clicked LED
  - Right click erases at the clicked LED
"""

from __future__ import annotations

import pygame

from games.base_game import Game
from games.sound import play_beep
from games.sprite_store import Sprite, get_sprite_store, draw_sprite


class OverlayEditor(Game):
    def __init__(self, grid, sprite_name: str, w: int, h: int):
        super().__init__(grid)

        self.sprite_name = sprite_name
        self.w = w
        self.h = h

        self.store = get_sprite_store()
        self.sprite: Sprite = self.store.get_or_create(sprite_name, w, h)

        self.cx = 0
        self.cy = 0

        self.palette = [
            (255, 255, 255),
            (0, 0, 0),
            (255, 0, 0),
            (0, 255, 0),
            (0, 180, 255),
            (255, 220, 80),
            (255, 120, 180),
            (80, 80, 80),
        ]
        self.p_index = 0

    def _grid_to_sprite_xy(self, gx: int, gy: int) -> tuple[int, int] | None:
        """Map grid coords to sprite coords based on current editor layout."""
        # Sprite is drawn at (1,1)
        sx = gx - 1
        sy = gy - 1
        if 0 <= sx < self.w and 0 <= sy < self.h:
            return (sx, sy)
        return None

    def _screen_to_grid(self, sx: int, sy: int) -> tuple[int, int] | None:
        """Convert pygame screen pixel coords into LED grid coords.

        This uses the LEDGrid layout parameters, so clicks hit the actual LED cell.
        """
        try:
            lx = int((sx - self.grid.offset_x) / (self.grid.led_size + self.grid.led_spacing))
            ly = int((sy - self.grid.offset_y) / (self.grid.led_size + self.grid.led_spacing))
        except Exception:
            return None

        if 0 <= lx < self.grid.grid_size and 0 <= ly < self.grid.grid_size:
            return (lx, ly)
        return None

    def update(self, dt: float):
        pass

    def render(self):
        self.grid.clear((0, 0, 0))

        # Frame
        for x in range(self.w + 2):
            self.grid.set_pixel(x, 0, (40, 40, 40))
            self.grid.set_pixel(x, self.h + 1, (40, 40, 40))
        for y in range(self.h + 2):
            self.grid.set_pixel(0, y, (40, 40, 40))
            self.grid.set_pixel(self.w + 1, y, (40, 40, 40))

        # Sprite contents
        draw_sprite(self.grid, self.sprite, 1, 1)

        # Cursor
        cur_color = (255, 255, 0)
        gx = 1 + self.cx
        gy = 1 + self.cy
        self.grid.set_pixel(gx, gy, cur_color)

        # HUD / instructions (minimal on-grid)
        self.grid.render_text("ED", self.w + 3, 0, (180, 180, 180), scale=1)
        self.grid.render_text("C", self.w + 3, 6, (180, 180, 180), scale=1)
        self.grid.render_text("S", self.w + 3, 12, (180, 180, 180), scale=1)

        # palette swatch
        sw = self.palette[self.p_index]
        self.grid.set_pixel(self.w + 4, self.h, sw)

    def handle_input(self, keys, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = getattr(event, "pos", None)
                if pos is not None:
                    grid_xy = self._screen_to_grid(pos[0], pos[1])
                    if grid_xy is not None:
                        sprite_xy = self._grid_to_sprite_xy(grid_xy[0], grid_xy[1])
                        if sprite_xy is not None:
                            self.cx, self.cy = sprite_xy
                            if event.button == 1:
                                self.sprite.set(self.cx, self.cy, self.palette[self.p_index])
                                play_beep(660, 15)
                            elif event.button == 3:
                                self.sprite.set(self.cx, self.cy, None)
                                play_beep(320, 15)
                continue

            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                self.running = False
                return

            if event.key == pygame.K_LEFT:
                self.cx = max(0, self.cx - 1)
            elif event.key == pygame.K_RIGHT:
                self.cx = min(self.w - 1, self.cx + 1)
            elif event.key == pygame.K_UP:
                self.cy = max(0, self.cy - 1)
            elif event.key == pygame.K_DOWN:
                self.cy = min(self.h - 1, self.cy + 1)
            elif event.key == pygame.K_c:
                self.p_index = (self.p_index + 1) % len(self.palette)
                play_beep(520, 20)
            elif event.key == pygame.K_SPACE:
                self.sprite.set(self.cx, self.cy, self.palette[self.p_index])
                play_beep(660, 20)
            elif event.key == pygame.K_BACKSPACE:
                self.sprite.set(self.cx, self.cy, None)
                play_beep(320, 20)
            elif event.key == pygame.K_s:
                self.store.save()
                play_beep(880, 40)