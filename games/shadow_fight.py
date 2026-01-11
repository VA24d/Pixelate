"""Shadow Fight (Stick) - simplified 1v1 stick fighter for a 19x19 grid.

This is a *very* small homage: two stick figures, simple movement, jump, and punch.

Controls:
  - A/D: move left/right
  - W: jump
  - J: punch
  - SPACE: restart after game over
  - ESC: return to menu

Gameplay:
  - Land punches to reduce opponent HP
  - First to 0 HP loses
"""

from __future__ import annotations

import math
import random
import pygame

from games.base_game import Game
from games.sound import play_beep


class ShadowFight(Game):
    def __init__(self, grid):
        super().__init__(grid)

        self.ground_y = 15
        self.gravity = 24.0
        self.jump_v = -10.0

        self._reset()

    def _reset(self):
        self.game_over = False
        self.winner = None

        self.p1_x = 5.0
        self.p1_y = float(self.ground_y)
        self.p1_vy = 0.0
        self.p1_hp = 10
        self.p1_attack_cd = 0.0
        self.p1_attack_timer = 0.0

        self.ai_x = 13.0
        self.ai_y = float(self.ground_y)
        self.ai_vy = 0.0
        self.ai_hp = 10
        self.ai_attack_cd = 0.0
        self.ai_attack_timer = 0.0

        self._t = 0.0

    def update(self, dt: float):
        if self.game_over:
            return

        self._t += dt
        self.p1_attack_cd = max(0.0, self.p1_attack_cd - dt)
        self.ai_attack_cd = max(0.0, self.ai_attack_cd - dt)
        self.p1_attack_timer = max(0.0, self.p1_attack_timer - dt)
        self.ai_attack_timer = max(0.0, self.ai_attack_timer - dt)

        # Physics
        self._apply_physics(dt)

        # AI
        self._update_ai(dt)

        # Hits
        self._resolve_hits()

        # Win check
        if self.p1_hp <= 0:
            self.game_over = True
            self.winner = "AI"
            play_beep(220, 200)
        elif self.ai_hp <= 0:
            self.game_over = True
            self.winner = "YOU"
            play_beep(880, 120)

    def _apply_physics(self, dt: float):
        # P1
        self.p1_vy += self.gravity * dt
        self.p1_y += self.p1_vy * dt
        if self.p1_y >= self.ground_y:
            self.p1_y = float(self.ground_y)
            self.p1_vy = 0.0

        # AI
        self.ai_vy += self.gravity * dt
        self.ai_y += self.ai_vy * dt
        if self.ai_y >= self.ground_y:
            self.ai_y = float(self.ground_y)
            self.ai_vy = 0.0

    def _update_ai(self, dt: float):
        # Simple chase + occasional jump + punch when close.
        dist = self.ai_x - self.p1_x
        if abs(dist) > 2.5:
            self.ai_x += (-1 if dist > 0 else 1) * 2.2 * dt
        else:
            # Attack
            if self.ai_attack_cd <= 0:
                self.ai_attack_timer = 0.18
                self.ai_attack_cd = 0.6
                play_beep(620, 25)

        # Small random jumps
        if self.ai_y >= self.ground_y and random.random() < 0.01:
            self.ai_vy = self.jump_v

        self.ai_x = max(1.0, min(self.grid.grid_size - 2.0, self.ai_x))

    def _resolve_hits(self):
        # P1 punch range
        if self.p1_attack_timer > 0:
            if abs(self.ai_x - self.p1_x) <= 2.0 and abs(self.ai_y - self.p1_y) <= 2.5:
                self.ai_hp -= 1
                self.p1_attack_timer = 0.0
                play_beep(880, 20)

        # AI punch range
        if self.ai_attack_timer > 0:
            if abs(self.ai_x - self.p1_x) <= 2.0 and abs(self.ai_y - self.p1_y) <= 2.5:
                self.p1_hp -= 1
                self.ai_attack_timer = 0.0
                play_beep(320, 20)

    def render(self):
        # Arena background
        self.grid.clear((5, 0, 10))

        # Ground line
        for x in range(self.grid.grid_size):
            self.grid.set_pixel(x, self.ground_y + 1, (40, 40, 40))

        # Fighters
        p1_color = (255, 60, 60)
        ai_color = (60, 160, 255)
        self._draw_stick(
            int(round(self.p1_x)),
            int(round(self.p1_y)),
            p1_color,
            facing=1,
            punching=self.p1_attack_timer > 0,
        )
        self._draw_stick(
            int(round(self.ai_x)),
            int(round(self.ai_y)),
            ai_color,
            facing=-1,
            punching=self.ai_attack_timer > 0,
        )

        # HP bars
        self._draw_hp(1, 0, self.p1_hp, p1_color)
        self._draw_hp(10, 0, self.ai_hp, ai_color)

        self.grid.render_text("VS", 7, 0, (255, 255, 0), scale=1)

        if self.game_over:
            self.grid.render_text(self.winner, 2, 7, (255, 255, 0), scale=1)
            self.grid.render_text("WINS", 2, 12, (255, 255, 255), scale=1)

    def _draw_hp(self, x: int, y: int, hp: int, color: tuple[int, int, int]):
        hp = max(0, min(10, hp))
        dim = (max(10, color[0] // 5), max(10, color[1] // 5), max(10, color[2] // 5))
        for i in range(9):
            self.grid.set_pixel(x + i, y + 2, dim)
        for i in range(hp):
            self.grid.set_pixel(x + i, y + 2, color)

    def _draw_stick(self, x: int, y: int, color: tuple[int, int, int], facing: int, punching: bool):
        """Draw a tiny stick figure anchored at feet (x,y)."""
        # Head
        self.grid.set_pixel(x, y - 5, color)
        # Body
        for dy in range(1, 4):
            self.grid.set_pixel(x, y - (5 - dy), color)

        # Legs
        self.grid.set_pixel(x - 1, y - 1, color)
        self.grid.set_pixel(x + 1, y - 1, color)
        self.grid.set_pixel(x - 1, y, color)
        self.grid.set_pixel(x + 1, y, color)

        # Arms
        arm_y = y - 3
        self.grid.set_pixel(x - 1, arm_y, color)
        self.grid.set_pixel(x + 1, arm_y, color)

        if punching:
            # Extend one arm forward
            self.grid.set_pixel(x + 2 * facing, arm_y, color)
            self.grid.set_pixel(x + 3 * facing, arm_y, color)

    def handle_input(self, keys, events):
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                self.running = False
                return

            if self.game_over:
                if event.key == pygame.K_SPACE:
                    self._reset()
                continue

            if event.key == pygame.K_w:
                if self.p1_y >= self.ground_y:
                    self.p1_vy = self.jump_v
                    play_beep(520, 25)
            elif event.key == pygame.K_j:
                if self.p1_attack_cd <= 0:
                    self.p1_attack_timer = 0.18
                    self.p1_attack_cd = 0.5
                    play_beep(740, 20)

        # Continuous movement
        if not self.game_over:
            speed = 4.0
            if keys[pygame.K_a]:
                self.p1_x -= speed * (1 / 60)
            if keys[pygame.K_d]:
                self.p1_x += speed * (1 / 60)
            self.p1_x = max(1.0, min(self.grid.grid_size - 2.0, self.p1_x))