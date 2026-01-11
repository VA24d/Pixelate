"""Asphalt Racing (2D pseudo-3D) - tiny endless runner racer for a 19x19 LED grid.

This is an *inspired by Asphalt* arcade racer, scaled down to 19x19:
  - Road scrolls toward the player with perspective (narrow at horizon, wide at bottom)
  - You steer left/right and control speed
  - Avoid traffic cars; passing cars increases score

Controls:
  - LEFT/RIGHT: steer
  - UP: accelerate
  - DOWN: brake
  - SPACE: restart after crash
  - ESC: return to menu
"""

from __future__ import annotations

import random
import pygame

from games.base_game import Game
from games.sound import play_beep
from games.sprite_store import get_sprite_store, draw_sprite


class AsphaltRace(Game):
    def __init__(self, grid):
        super().__init__(grid)

        self._sprite_store = get_sprite_store()

        # Road geometry
        self.horizon_y = 4
        self.road_center = self.grid.grid_size // 2
        self.curve = 0.0  # positive curves road to the right (visual)

        # Player
        self.player_x = 0.0  # offset from road center, in pixels
        self.player_lane_w = 3.0

        # Speed
        self.speed = 7.5
        self.min_speed = 3.0
        self.max_speed = 13.0

        # Controls tuning
        self.steer_speed = 9.0  # pixels/sec (higher = easier dodging)
        self.accel_per_s = 8.0

        self._last_dt = 1 / 60

        # World scroll and distance
        self.scroll = 0.0
        self.distance = 0.0
        self.score = 0

        # Traffic
        self.traffic = []
        self._spawn_cd = 0.0

        self.crashed = False
        self._reset()

    def _reset(self) -> None:
        self.player_x = 0.0
        self.curve = 0.0
        self.speed = 7.5
        self.scroll = 0.0
        self.distance = 0.0
        self.score = 0
        self.traffic = []
        self._spawn_cd = 0.4
        self.crashed = False

    # --- Simulation helpers (unit-test friendly) ---
    def _road_half_width(self, y: int) -> int:
        """Half-road width at row y (perspective)."""
        y = max(0, min(self.grid.grid_size - 1, y))
        # At horizon: narrow. At bottom: wide.
        t = 0.0
        if y > self.horizon_y:
            t = (y - self.horizon_y) / max(1, (self.grid.grid_size - 1 - self.horizon_y))
        # half-width from 3..8
        return int(round(3 + 5 * t))

    def _road_center_at(self, y: int) -> int:
        # Visual curve stronger near bottom.
        if y <= self.horizon_y:
            return self.road_center
        t = (y - self.horizon_y) / max(1, (self.grid.grid_size - 1 - self.horizon_y))
        return int(round(self.road_center + self.curve * t * t))

    def _player_world_y(self) -> float:
        # Player is near the bottom.
        return float(self.grid.grid_size - 3)

    def _player_pos(self) -> tuple[int, int]:
        py = int(self._player_world_y())
        cx = self._road_center_at(py)
        px = int(round(cx + self.player_x))
        return (px, py)

    def _spawn_traffic(self) -> None:
        # Spawn near horizon; choose lane-ish offset.
        # Keep within road width at horizon.
        hw = self._road_half_width(self.horizon_y + 1)
        lane_offsets = [-3, 0, 3]
        ox = random.choice(lane_offsets)
        ox = max(-hw + 1, min(hw - 1, ox))
        self.traffic.append({"x": float(ox), "y": float(self.horizon_y + 1), "passed": False})

    def _update_traffic(self, dt: float) -> None:
        # Traffic moves downward relative to the player.
        for car in self.traffic:
            car["y"] += self.speed * dt * 1.4

        # Remove cars that leave the screen, award score if passed.
        kept = []
        for car in self.traffic:
            if car["y"] > self.grid.grid_size + 1:
                if car.get("passed"):
                    self.score += 1
                continue
            kept.append(car)
        self.traffic = kept

    def _check_collision(self) -> bool:
        px, py = self._player_pos()
        for car in self.traffic:
            cy = int(round(car["y"]))
            if abs(cy - py) > 1:
                continue
            # compute car screen x at this y
            cx = self._road_center_at(cy) + int(round(car["x"]))
            if abs(cx - px) <= 1:
                return True
        return False

    def update(self, dt: float):
        # Remember dt for input integration (handle_input doesn't receive dt).
        try:
            self._last_dt = float(dt)
        except Exception:
            self._last_dt = 1 / 60
        self._last_dt = max(1 / 240, min(1 / 15, self._last_dt))

        if self.crashed:
            return

        # Integrate distance and scroll
        self.distance += self.speed * dt
        self.scroll += self.speed * dt

        # Gentle random curve changes
        self.curve += random.uniform(-0.7, 0.7) * dt
        self.curve = max(-5.0, min(5.0, self.curve))

        # Spawn traffic (more frequent at higher speed)
        self._spawn_cd -= dt
        if self._spawn_cd <= 0.0:
            self._spawn_traffic()
            interval = max(0.35, 1.1 - (self.speed - self.min_speed) * 0.09)
            self._spawn_cd = interval

        self._update_traffic(dt)

        # Mark traffic as passed when it goes below player.
        py = self._player_world_y()
        for car in self.traffic:
            if not car.get("passed") and car["y"] > py + 0.5:
                car["passed"] = True

        # Collision
        if self._check_collision():
            self.crashed = True
            play_beep(220, 180)

    def render(self):
        # Background sky
        self.grid.clear((0, 0, 18))

        # Draw road
        for y in range(self.horizon_y, self.grid.grid_size):
            center = self._road_center_at(y)
            hw = self._road_half_width(y)

            # grass
            for x in range(self.grid.grid_size):
                if x < center - hw or x > center + hw:
                    self.grid.set_pixel(x, y, (0, 40, 0))
                else:
                    self.grid.set_pixel(x, y, (25, 25, 25))

            # road edge lines
            self.grid.set_pixel(center - hw, y, (220, 220, 220))
            self.grid.set_pixel(center + hw, y, (220, 220, 220))

            # center dashed line
            if y > self.horizon_y and (int(self.scroll * 6) + y) % 4 == 0:
                self.grid.set_pixel(center, y, (255, 220, 80))

        # Draw traffic cars (simple 2x2)
        for car in self.traffic:
            cy = int(round(car["y"]))
            if cy < 0 or cy >= self.grid.grid_size:
                continue
            cx = self._road_center_at(cy) + int(round(car["x"]))
            c1 = (255, 60, 60)
            c2 = (200, 20, 20)
            self.grid.set_pixel(cx, cy, c1)
            self.grid.set_pixel(cx + 1, cy, c2)
            self.grid.set_pixel(cx, cy + 1, c2)
            self.grid.set_pixel(cx + 1, cy + 1, c1)

        # Draw player car near bottom (2x2)
        px, py = self._player_pos()
        p1 = (60, 200, 255)
        p2 = (20, 120, 200)
        self.grid.set_pixel(px, py, p1)
        self.grid.set_pixel(px + 1, py, p2)
        self.grid.set_pixel(px, py + 1, p2)
        self.grid.set_pixel(px + 1, py + 1, p1)

        # HUD (user-editable sprites)
        sprite = self._sprite_store.get("hud_race_dist")
        if sprite is not None:
            draw_sprite(self.grid, sprite, 0, 0)
        else:
            self.grid.render_text("R", 0, 0, (120, 200, 255), scale=1)
        self.grid.render_number(int(self.distance) % 100, 4, 0, (255, 255, 255), scale=1)
        sprite = self._sprite_store.get("hud_race_score")
        if sprite is not None:
            draw_sprite(self.grid, sprite, 0, 6)
        else:
            self.grid.render_text("S", 0, 6, (255, 220, 80), scale=1)
        self.grid.render_number(self.score % 100, 4, 6, (255, 255, 255), scale=1)

        if self.crashed:
            self.grid.render_text("CRASH", 0, 12, (255, 255, 0), scale=1)
            self.grid.render_text("SP", 6, 18 - 5, (150, 150, 150), scale=1)

    def handle_input(self, keys, events):
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                self.running = False
                return

            if self.crashed:
                if event.key == pygame.K_SPACE:
                    self._reset()
                continue

        # Continuous steering / speed
        if not self.crashed:
            # dt is not passed to handle_input in this architecture, so we use
            # dt from update().
            dt = getattr(self, "_last_dt", 1 / 60)

            steer = 0.0
            if keys[pygame.K_LEFT]:
                steer -= 1.0
            if keys[pygame.K_RIGHT]:
                steer += 1.0

            accel = 0.0
            if keys[pygame.K_UP]:
                accel += 1.0
            if keys[pygame.K_DOWN]:
                accel -= 1.0

            # Apply
            self.player_x += steer * self.steer_speed * dt
            self.speed += accel * self.accel_per_s * dt
            self.speed = max(self.min_speed, min(self.max_speed, self.speed))

            # Keep player within road bounds (bottom row)
            py = int(self._player_world_y())
            center = self._road_center_at(py)
            hw = self._road_half_width(py)
            px = center + self.player_x
            px = max(center - hw + 1, min(center + hw - 2, px))
            self.player_x = px - center