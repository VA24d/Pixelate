"""Menu Card Editor: live pixel editing for per-game carousel card overlays.

User goal: edit the *logo + text pixels you see* on the carousel card.

We implement this as a per-game overlay sprite named:
  menu_card_<GAME>

Sprite size is 19x17 and is drawn starting at grid position (0,2), so it covers:
  - the game number (y=2)
  - the card border/logo/name area (y=4..18)

The top 2 rows (y=0..1) are reserved for editor UI (palette), so they do not
affect the stored sprite.

Controls:
  - Click a pixel in the card to paint
  - Right click to erase
  - Click a palette swatch to change color
  - Arrow keys move cursor
  - SPACE paints
  - BACKSPACE erases
  - C cycles palette
  - S saves
  - ESC exits editor
"""

from __future__ import annotations

import pygame

from games.base_game import Game
from games.menu import CarouselMenu
from games.sound import play_beep
from games.sprite_store import Sprite, get_sprite_store, draw_sprite


class MenuCardEditor(Game):
    def __init__(self, grid, game_index: int):
        super().__init__(grid)

        self.game_index = int(game_index)

        self.store = get_sprite_store()

        # Overlay sprite covers y=2..18 (17 rows)
        self.sprite_name = ""
        try:
            # CarouselMenu is the source of truth for names.
            tmp_menu = CarouselMenu(self.grid, game_manager=None)
            self.sprite_name = f"menu_card_{tmp_menu.games[self.game_index]['name']}"
        except Exception:
            self.sprite_name = f"menu_card_{self.game_index}"

        self.w = 19
        self.h = 17
        self.sprite: Sprite = self.store.get_or_create(self.sprite_name, self.w, self.h)

        # Cursor inside overlay sprite
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

        # Use menu renderer to show a live card preview underneath.
        self._menu_preview = CarouselMenu(self.grid, game_manager=None)

        # If user wants to start from the existing card, they can bake it.
        # (We avoid doing this automatically to keep the overlay non-destructive.)

    def _bake_from_base(self) -> None:
        """Bake the current base card render into the overlay sprite.

        This gives you a full starting point to tweak pixels from.
        """
        saved_overlay = None
        try:
            # Temporarily remove our overlay from the store so menu render doesn't include it.
            saved_overlay = getattr(self.store, "_sprites", {}).pop(self.sprite_name, None)

            self.grid.clear((0, 0, 0))
            self._menu_preview._render_game_card(self.game_index, float(self.game_index))

            for y in range(self.h):
                for x in range(self.w):
                    c = self.grid.get_pixel(x, y + 2)
                    if c != (0, 0, 0):
                        self.sprite.set(x, y, c)
                    else:
                        self.sprite.set(x, y, None)
        finally:
            if saved_overlay is not None:
                getattr(self.store, "_sprites", {})[self.sprite_name] = saved_overlay

    def _screen_to_grid(self, sx: int, sy: int) -> tuple[int, int] | None:
        try:
            lx = int((sx - self.grid.offset_x) / (self.grid.led_size + self.grid.led_spacing))
            ly = int((sy - self.grid.offset_y) / (self.grid.led_size + self.grid.led_spacing))
        except Exception:
            return None

        if 0 <= lx < self.grid.grid_size and 0 <= ly < self.grid.grid_size:
            return (lx, ly)
        return None

    def _grid_to_overlay_xy(self, gx: int, gy: int) -> tuple[int, int] | None:
        # Overlay starts at y=2
        if gy < 2:
            return None
        sx = gx
        sy = gy - 2
        if 0 <= sx < self.w and 0 <= sy < self.h:
            return (sx, sy)
        return None

    def update(self, dt: float):
        pass

    def render(self):
        # Render base card
        self._menu_preview.grid = self.grid
        self._menu_preview.grid.clear((0, 0, 0))
        # Draw ONLY the selected card centered (x_shift=0)
        self._menu_preview._render_game_card(self.game_index, float(self.game_index))

        # Apply overlay sprite
        draw_sprite(self.grid, self.sprite, 0, 2)

        # Palette UI on top row (y=0)
        for i, c in enumerate(self.palette):
            if i >= self.grid.grid_size:
                break
            self.grid.set_pixel(i, 0, c)
            # selection marker
            self.grid.set_pixel(i, 1, (255, 255, 0) if i == self.p_index else (20, 20, 20))

        # Cursor highlight (within overlay area)
        cur_gx = self.cx
        cur_gy = self.cy + 2
        self.grid.set_pixel(cur_gx, cur_gy, (255, 255, 0))

    def handle_input(self, keys, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = getattr(event, "pos", None)
                if pos is None:
                    continue

                grid_xy = self._screen_to_grid(pos[0], pos[1])
                if grid_xy is None:
                    continue

                gx, gy = grid_xy

                # Palette selection clicks (row 0)
                if gy == 0 and 0 <= gx < len(self.palette):
                    self.p_index = gx
                    play_beep(520, 20)
                    continue

                overlay_xy = self._grid_to_overlay_xy(gx, gy)
                if overlay_xy is None:
                    continue

                self.cx, self.cy = overlay_xy
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
            elif event.key == pygame.K_b:
                self._bake_from_base()
                play_beep(740, 60)