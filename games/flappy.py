"""Flappy Bird - simplified for a 19x19 LED grid.

Controls:
  - SPACE: flap
  - R: restart after game over
  - ESC: return to menu

Gameplay:
  - Gravity pulls you down
  - Passing pipes increases score
  - Endless score-until-death
"""

from __future__ import annotations

import random
import pygame

from games.base_game import Game
from games.sound import play_beep


class Flappy(Game):
    def __init__(self, grid):
        super().__init__(grid)

        self.gravity = 18.0
        self.flap_velocity = -7.0
        self.pipe_speed = 7.0
        self.gap_size = 6

        self._reset()

    def _reset(self):
        self.score = 0
        self.game_over = False

        self.bird_x = 5
        self.bird_y = float(self.grid.grid_size // 2)
        self.bird_vy = 0.0

        # Pipes: each pipe is x position + gap center y
        self.pipes = []
        self._spawn_pipe(self.grid.grid_size + 2)
        self._spawn_pipe(self.grid.grid_size + 10)

        self._passed = set()

    def _spawn_pipe(self, x: float):
        gap_center = random.randint(5, self.grid.grid_size - 6)
        self.pipes.append({"x": float(x), "gap": gap_center})

    def update(self, dt: float):
        if self.game_over:
            return

        # Bird physics
        self.bird_vy += self.gravity * dt
        self.bird_y += self.bird_vy * dt

        # Pipes movement
        for p in self.pipes:
            p["x"] -= self.pipe_speed * dt

        # Recycle pipes
        while self.pipes and self.pipes[0]["x"] < -2:
            self.pipes.pop(0)
            self._spawn_pipe(self.grid.grid_size + 2)

        # Collisions / scoring
        if self.bird_y < 0 or self.bird_y > self.grid.grid_size - 1:
            self._die()
            return

        by = int(round(self.bird_y))

        for p in self.pipes:
            px = int(round(p["x"]))
            if px == self.bird_x:
                gap_top = p["gap"] - self.gap_size // 2
                gap_bot = p["gap"] + self.gap_size // 2
                if not (gap_top <= by <= gap_bot):
                    self._die()
                    return

            # Score when pipe passes bird
            if p["x"] < self.bird_x and id(p) not in self._passed:
                self._passed.add(id(p))
                self.score += 1
                play_beep(880, 45)

    def _die(self):
        self.game_over = True
        play_beep(220, 150)

    def render(self):
        # Sky background
        self.grid.clear((0, 0, 25))

        # Pipes
        pipe_color = (0, 200, 80)
        for p in self.pipes:
            px = int(round(p["x"]))
            gap_top = p["gap"] - self.gap_size // 2
            gap_bot = p["gap"] + self.gap_size // 2
            for y in range(0, self.grid.grid_size):
                if y < gap_top or y > gap_bot:
                    # pipe body
                    self.grid.set_pixel(px, y, pipe_color)
                    # thickness
                    self.grid.set_pixel(px + 1, y, (0, 150, 60))

        # Bird (2x2)
        bx = self.bird_x
        by = int(round(self.bird_y))
        bird = (255, 230, 60)
        self.grid.set_pixel(bx, by, bird)
        self.grid.set_pixel(bx, by + 1, bird)
        self.grid.set_pixel(bx + 1, by, (255, 180, 0))
        self.grid.set_pixel(bx + 1, by + 1, (255, 180, 0))

        # Score
        self.grid.render_text("F", 0, 0, (120, 200, 255), scale=1)
        self.grid.render_number(self.score, 4, 0, (255, 255, 255), scale=1)

        if self.game_over:
            self.grid.render_text("OVER", 2, 7, (255, 255, 0), scale=1)
            self.grid.render_text("R", 8, 13, (150, 150, 150), scale=1)

    def handle_input(self, keys, events):
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                self.running = False
                return

            if self.game_over:
                if event.key == pygame.K_r:
                    self._reset()
                continue

            if event.key == pygame.K_SPACE:
                self.bird_vy = self.flap_velocity
                play_beep(660, 30)
