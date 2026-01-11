"""Snake - classic snake on a 19x19 LED grid.

Controls:
  - Arrow keys: change direction
  - SPACE: restart after game over
  - ESC: return to menu

Gameplay:
  - Eat food to grow
  - Wrap at edges (left-right, top-bottom)
  - Die if you hit yourself
  - Endless score-until-death
"""

from __future__ import annotations

import random
import pygame
from typing import Deque, List, Tuple
from collections import deque

from games.base_game import Game
from games.sound import play_beep


Pos = Tuple[int, int]


class Snake(Game):
    def __init__(self, grid):
        super().__init__(grid)

        self.tick_rate = 8.0  # moves per second
        self._accum = 0.0

        self.game_over = False
        self.score = 0

        self.direction: Pos = (1, 0)
        self.next_direction: Pos = (1, 0)

        self.snake: Deque[Pos] = deque()
        self.food: Pos = (0, 0)
        self._reset()

    def _reset(self):
        self.game_over = False
        self.score = 0

        cx = self.grid.grid_size // 2
        cy = self.grid.grid_size // 2
        self.snake = deque([(cx - 1, cy), (cx, cy), (cx + 1, cy)])
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self._accum = 0.0

        self._spawn_food()

    def _spawn_food(self):
        free: List[Pos] = [
            (x, y)
            for y in range(self.grid.grid_size)
            for x in range(self.grid.grid_size)
            if (x, y) not in self.snake
        ]
        self.food = random.choice(free) if free else (0, 0)

    def update(self, dt: float):
        if self.game_over:
            return
        self._accum += dt
        step = 1.0 / self.tick_rate
        while self._accum >= step:
            self._accum -= step
            self._step()

    def _step(self):
        # Apply buffered direction
        self.direction = self.next_direction

        hx, hy = self.snake[-1]
        dx, dy = self.direction
        nx = (hx + dx) % self.grid.grid_size
        ny = (hy + dy) % self.grid.grid_size

        new_head = (nx, ny)

        # Self collision (allow moving into tail only if it will move away)
        tail = self.snake[0]
        body = set(self.snake)
        will_grow = new_head == self.food
        if new_head in body and (not (new_head == tail and not will_grow)):
            self._die()
            return

        self.snake.append(new_head)

        # Eat
        if will_grow:
            self.score += 1
            play_beep(880, 60)
            self._spawn_food()
        else:
            self.snake.popleft()

    def _die(self):
        self.game_over = True
        play_beep(220, 150)

    def render(self):
        self.grid.clear((0, 0, 0))

        # Food
        fx, fy = self.food
        self.grid.set_pixel(fx, fy, (255, 60, 60))

        # Snake
        for i, (x, y) in enumerate(self.snake):
            # Head brighter
            if i == len(self.snake) - 1:
                self.grid.set_pixel(x, y, (0, 255, 0))
            else:
                self.grid.set_pixel(x, y, (0, 150, 0))

        # Score
        self.grid.render_text("S", 0, 0, (120, 255, 120), scale=1)
        self.grid.render_number(self.score, 4, 0, (255, 255, 255), scale=1)

        if self.game_over:
            self.grid.render_text("OVER", 2, 7, (255, 255, 0), scale=1)
            self.grid.render_text("SP", 6, 13, (150, 150, 150), scale=1)

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

            if event.key == pygame.K_UP:
                self._set_next_dir((0, -1))
            elif event.key == pygame.K_DOWN:
                self._set_next_dir((0, 1))
            elif event.key == pygame.K_LEFT:
                self._set_next_dir((-1, 0))
            elif event.key == pygame.K_RIGHT:
                self._set_next_dir((1, 0))

    def _set_next_dir(self, d: Pos):
        # Prevent instant 180 degree turns
        dx, dy = self.direction
        ndx, ndy = d
        if dx == -ndx and dy == -ndy:
            return
        self.next_direction = d
        play_beep(520, 20)