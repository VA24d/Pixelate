"""Font editor: live 3x5 glyph editing for LEDGrid.render_text().

The UX is intentionally on-grid (no reliance on small pygame text).

Modes:
  - Atlas view: shows a page of glyphs; click a glyph to edit
  - Edit view: magnified 3x5 editor so clicks are obvious

Controls (both modes):
  - Type a character (A-Z, 0-9, space, '-') to jump to it
  - TAB: toggle Atlas/Edit
  - ESC: exit editor

Atlas view:
  - Click a glyph to edit
  - N / P: next / previous atlas page

Edit view:
  - Arrow keys: move cursor
  - SPACE: toggle pixel
  - BACKSPACE: clear pixel
  - S: save overrides
  - R: reset glyph (remove override)
"""

from __future__ import annotations

import pygame

from games.base_game import Game
from games.font_store import FontOverrides, Glyph, get_font_store
from games.sound import play_beep


def _blank_glyph() -> Glyph:
    return [[0, 0, 0] for _ in range(5)]


def _copy_glyph(g: Glyph) -> Glyph:
    return [[int(v) for v in row] for row in g]


class FontEditor(Game):
    def __init__(self, grid, initial_char: str = "A"):
        super().__init__(grid)

        self.store = get_font_store()

        self.charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -"
        self.char_index = 0
        self.set_current_char(initial_char)

        self.mode = "atlas"  # atlas | edit
        self.atlas_page = 0

        self.cx = 0
        self.cy = 0

        self._load_current_glyph()

    def _current_char(self) -> str:
        return self.charset[self.char_index]

    def set_current_char(self, ch: str) -> None:
        ch = str(ch).upper()
        if ch in self.charset:
            self.char_index = self.charset.index(ch)
        else:
            self.char_index = 0

    def _load_current_glyph(self) -> None:
        ch = self._current_char()
        g = self.store.get_glyph(ch)
        self.glyph = _copy_glyph(g) if g is not None else _blank_glyph()

    def _preview_overrides(self) -> FontOverrides:
        overrides = self.store.get_overrides()
        overrides[self._current_char()] = _copy_glyph(self.glyph)
        return overrides

    def _save_current_glyph(self) -> None:
        self.store.set_glyph(self._current_char(), self.glyph)
        self.store.save()

    def _reset_current_glyph(self) -> None:
        self.store.clear_glyph(self._current_char())
        self.store.save()
        self.glyph = _blank_glyph()

    def _screen_to_grid(self, sx: int, sy: int) -> tuple[int, int] | None:
        try:
            lx = int((sx - self.grid.offset_x) / (self.grid.led_size + self.grid.led_spacing))
            ly = int((sy - self.grid.offset_y) / (self.grid.led_size + self.grid.led_spacing))
        except Exception:
            return None
        if 0 <= lx < self.grid.grid_size and 0 <= ly < self.grid.grid_size:
            return (lx, ly)
        return None

    def _atlas_layout(self) -> tuple[int, int, int, int]:
        """Return (ox, oy, cell_w, cell_h) for atlas cells."""
        return (0, 0, 4, 6)  # 3x5 glyph + 1 spacing

    def _atlas_page_size(self) -> int:
        # 4 columns * 3 rows
        return 12

    def _atlas_items(self) -> list[str]:
        page_size = self._atlas_page_size()
        start = self.atlas_page * page_size
        end = start + page_size
        return list(self.charset[start:end])

    def _grid_to_atlas_char(self, gx: int, gy: int) -> str | None:
        ox, oy, cw, ch = self._atlas_layout()
        if gx < ox or gy < oy:
            return None

        col = (gx - ox) // cw
        row = (gy - oy) // ch
        if col < 0 or col >= 4 or row < 0 or row >= 3:
            return None

        idx = int(row * 4 + col)
        items = self._atlas_items()
        if idx < 0 or idx >= len(items):
            return None

        # ensure click is within 3x5 glyph area (not in spacing gutter)
        lx = (gx - ox) % cw
        ly = (gy - oy) % ch
        if lx >= 3 or ly >= 5:
            return None
        return items[idx]

    def _editor_layout(self) -> tuple[int, int, int]:
        """Return (ox, oy, scale) for magnified editor."""
        return (1, 1, 3)

    def _grid_to_glyph_xy(self, gx: int, gy: int) -> tuple[int, int] | None:
        ox, oy, scale = self._editor_layout()
        x = gx - ox
        y = gy - oy
        if x < 0 or y < 0:
            return None
        if x >= 3 * scale or y >= 5 * scale:
            return None
        return (x // scale, y // scale)

    def update(self, dt: float):
        pass

    def render(self):
        self.grid.clear((0, 0, 0))

        # Ensure preview text uses current (unsaved) edits.
        try:
            self.grid.set_font_overrides(self._preview_overrides())
        except Exception:
            pass

        if self.mode == "atlas":
            self._render_atlas()
        else:
            self._render_editor()

    def handle_input(self, keys, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = getattr(event, "pos", None)
                if pos is not None:
                    grid_xy = self._screen_to_grid(pos[0], pos[1])
                    if grid_xy is not None:
                        if self.mode == "atlas":
                            ch = self._grid_to_atlas_char(grid_xy[0], grid_xy[1])
                            if ch is not None:
                                self.set_current_char(ch)
                                self._load_current_glyph()
                                self.mode = "edit"
                                play_beep(740, 20)
                        else:
                            glyph_xy = self._grid_to_glyph_xy(grid_xy[0], grid_xy[1])
                            if glyph_xy is not None:
                                self.cx, self.cy = glyph_xy
                                self.glyph[self.cy][self.cx] = 0 if self.glyph[self.cy][self.cx] else 1
                                play_beep(660, 15)
                continue

            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                self.running = False
                return

            if event.key == pygame.K_TAB:
                self.mode = "edit" if self.mode == "atlas" else "atlas"
                play_beep(520, 20)
                continue

            # direct jump by typing a character
            typed = getattr(event, "unicode", "")
            if typed:
                ch = str(typed).upper()
                if ch in self.charset:
                    self.set_current_char(ch)
                    self._load_current_glyph()
                    self.mode = "edit"
                    play_beep(520, 20)
                    continue

            if self.mode == "atlas":
                if event.key == pygame.K_n:
                    self.atlas_page = (self.atlas_page + 1) % max(1, (len(self.charset) + 11) // 12)
                    play_beep(520, 25)
                elif event.key == pygame.K_p:
                    self.atlas_page = (self.atlas_page - 1) % max(1, (len(self.charset) + 11) // 12)
                    play_beep(420, 25)
                continue

            # edit mode controls
            if event.key == pygame.K_LEFT:
                self.cx = max(0, self.cx - 1)
            elif event.key == pygame.K_RIGHT:
                self.cx = min(2, self.cx + 1)
            elif event.key == pygame.K_UP:
                self.cy = max(0, self.cy - 1)
            elif event.key == pygame.K_DOWN:
                self.cy = min(4, self.cy + 1)
            elif event.key == pygame.K_SPACE:
                self.glyph[self.cy][self.cx] = 0 if self.glyph[self.cy][self.cx] else 1
                play_beep(660, 15)
            elif event.key == pygame.K_BACKSPACE:
                self.glyph[self.cy][self.cx] = 0
                play_beep(320, 15)
            elif event.key == pygame.K_r:
                self._reset_current_glyph()
                play_beep(320, 40)
            elif event.key == pygame.K_s:
                self._save_current_glyph()
                play_beep(880, 40)

    def _render_atlas(self) -> None:
        ox, oy, cw, ch = self._atlas_layout()

        items = self._atlas_items()

        # background guide boxes and glyphs
        for idx, c in enumerate(items):
            col = idx % 4
            row = idx // 4
            bx = ox + col * cw
            by = oy + row * ch

            # subtle border for each glyph cell
            border = (40, 40, 40)
            for dx in range(0, 3):
                self.grid.set_pixel(bx + dx, by + 5, border)
            for dy in range(0, 5):
                self.grid.set_pixel(bx + 3, by + dy, border)

            # draw the glyph using render_text so overrides show up
            color = (120, 200, 255)
            if c == self._current_char():
                color = (255, 255, 0)
            self.grid.render_text(c, bx, by, color, scale=1, spacing=1)

        # small preview at bottom
        self.grid.render_text("TAB", 0, 14, (120, 120, 120), scale=1)
        self.grid.render_text("NP", 12, 14, (120, 120, 120), scale=1)
        self.grid.render_text("TYPE", 0, 18 - 5, (0, 255, 255), scale=1)

    def _render_editor(self) -> None:
        ox, oy, scale = self._editor_layout()

        # frame around magnified area
        frame = (40, 40, 40)
        self.grid.fill_rect(0, 0, 11, 17, (0, 0, 0))
        for x in range(0, 11):
            self.grid.set_pixel(x, 0, frame)
            self.grid.set_pixel(x, 16, frame)
        for y in range(0, 17):
            self.grid.set_pixel(0, y, frame)
            self.grid.set_pixel(10, y, frame)

        # magnified glyph pixels
        on_color = (0, 255, 255)
        for y in range(5):
            for x in range(3):
                if self.glyph[y][x]:
                    self.grid.fill_rect(ox + x * scale, oy + y * scale, scale, scale, on_color)

        # cursor box
        cx0 = ox + self.cx * scale
        cy0 = oy + self.cy * scale
        cursor = (255, 255, 0)
        for dx in range(scale):
            self.grid.set_pixel(cx0 + dx, cy0, cursor)
            self.grid.set_pixel(cx0 + dx, cy0 + scale - 1, cursor)
        for dy in range(scale):
            self.grid.set_pixel(cx0, cy0 + dy, cursor)
            self.grid.set_pixel(cx0 + scale - 1, cy0 + dy, cursor)

        # right-side info
        self.grid.render_text("CH", 12, 0, (140, 140, 140), scale=1)
        self.grid.render_text(self._current_char(), 16, 0, (255, 255, 255), scale=1)

        self.grid.render_text("TAB", 12, 6, (120, 120, 120), scale=1)
        self.grid.render_text("S", 12, 12, (120, 120, 120), scale=1)
        self.grid.render_text("R", 16, 12, (120, 120, 120), scale=1)

        # bottom preview
        sample = "GAMES"
        self.grid.render_text(sample, 0, 18 - 5, (0, 255, 255), scale=1)