"""Pet Game - simple tamagotchi-style pets on the 19x19 LED grid.

Controls:
  - LEFT/RIGHT: select pet (Dog/Cat/Dino)
  - A: feed
  - S: play
  - D: rest
  - ESC: return to menu

Mechanics:
  Each pet has 3 stats (0..10): hunger, happiness, energy.
  Stats decay over time; actions increase one stat while decreasing another.
"""

from __future__ import annotations

import pygame
from dataclasses import dataclass
from typing import Tuple

from games.base_game import Game
from games.sound import play_beep


Color = Tuple[int, int, int]


@dataclass
class PetState:
    name: str
    primary_color: Color
    accent_color: Color
    hunger: float = 7.0
    happiness: float = 7.0
    energy: float = 7.0


class PetGame(Game):
    """A tiny pet-care game with 3 selectable pets."""

    def __init__(self, grid):
        super().__init__(grid)

        self.pets = [
            PetState("DOG", (210, 150, 90), (255, 255, 255)),
            PetState("CAT", (180, 180, 180), (255, 120, 180)),
            PetState("DINO", (60, 200, 90), (255, 240, 120)),
        ]
        self.selected_index = 0

        # Stat decay tuning (per second)
        self.hunger_decay = 0.30
        self.happiness_decay = 0.18
        self.energy_decay = 0.22

        # Small UI feedback
        self.action_message = ""
        self.action_timer = 0.0

    def update(self, dt: float):
        pet = self.pets[self.selected_index]

        # Natural decay over time
        pet.hunger = self._clamp_stat(pet.hunger - self.hunger_decay * dt)
        pet.happiness = self._clamp_stat(pet.happiness - self.happiness_decay * dt)
        pet.energy = self._clamp_stat(pet.energy - self.energy_decay * dt)

        if self.action_timer > 0:
            self.action_timer = max(0.0, self.action_timer - dt)
            if self.action_timer == 0.0:
                self.action_message = ""

    def render(self):
        # Dark blue background for contrast
        self.grid.clear((0, 0, 10))

        pet = self.pets[self.selected_index]

        # Title / pet name
        self.grid.render_text("PETS", 2, 0, (120, 200, 255), scale=1)
        self.grid.render_text(pet.name, 2, 6, (0, 255, 255), scale=1)

        # Pet sprite
        if pet.name == "DOG":
            self._render_dog(4, 8, pet.primary_color, pet.accent_color)
        elif pet.name == "CAT":
            self._render_cat(4, 8, pet.primary_color, pet.accent_color)
        else:
            self._render_dino(4, 8, pet.primary_color, pet.accent_color)

        # Stats bars (H/HAP/E)
        stats_y = 18
        self._render_stat_bar(1, stats_y, int(round(pet.hunger)), (255, 180, 0))
        self._render_stat_bar(7, stats_y, int(round(pet.happiness)), (255, 80, 180))
        self._render_stat_bar(13, stats_y, int(round(pet.energy)), (80, 160, 255))

        # Labels (tiny)
        self.grid.set_pixel(1, stats_y - 1, (255, 180, 0))
        self.grid.set_pixel(7, stats_y - 1, (255, 80, 180))
        self.grid.set_pixel(13, stats_y - 1, (80, 160, 255))

        # Action message
        if self.action_message:
            # Keep it short so it fits. (3x5 font)
            self.grid.render_text(self.action_message, 1, 1, (255, 255, 0), scale=1)

        # Simple navigation hint arrows
        arrow_color = (120, 120, 120)
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
                play_beep(420, 35)
                self.selected_index = (self.selected_index - 1) % len(self.pets)
            elif event.key == pygame.K_RIGHT:
                play_beep(520, 35)
                self.selected_index = (self.selected_index + 1) % len(self.pets)
            elif event.key == pygame.K_a:
                self._feed()
            elif event.key == pygame.K_s:
                self._play()
            elif event.key == pygame.K_d:
                self._rest()

    # --- actions ---

    def _feed(self):
        pet = self.pets[self.selected_index]
        pet.hunger = self._clamp_stat(pet.hunger + 3.0)
        pet.energy = self._clamp_stat(pet.energy + 0.5)
        pet.happiness = self._clamp_stat(pet.happiness - 0.3)
        play_beep(660, 60)
        self._flash_message("FED")

    def _play(self):
        pet = self.pets[self.selected_index]
        pet.happiness = self._clamp_stat(pet.happiness + 3.0)
        pet.energy = self._clamp_stat(pet.energy - 1.2)
        pet.hunger = self._clamp_stat(pet.hunger - 0.8)
        play_beep(740, 60)
        self._flash_message("PLAY")

    def _rest(self):
        pet = self.pets[self.selected_index]
        pet.energy = self._clamp_stat(pet.energy + 3.0)
        pet.happiness = self._clamp_stat(pet.happiness + 0.4)
        pet.hunger = self._clamp_stat(pet.hunger - 0.5)
        play_beep(520, 60)
        self._flash_message("REST")

    def _render_left_arrow(self, x: int, y: int, color: Color):
        pts = [(0, 0), (1, -1), (1, 1), (2, -2), (2, 2)]
        for dx, dy in pts:
            self.grid.set_pixel(x + dx, y + dy, color)

    def _render_right_arrow(self, x: int, y: int, color: Color):
        pts = [(0, 0), (-1, -1), (-1, 1), (-2, -2), (-2, 2)]
        for dx, dy in pts:
            self.grid.set_pixel(x + dx, y + dy, color)

    def _flash_message(self, msg: str):
        self.action_message = msg
        self.action_timer = 0.8

    # --- rendering helpers ---

    def _render_stat_bar(self, x: int, y: int, value_0_to_10: int, color: Color):
        # 5 pixels wide bar (0..10 => 0..5 with half steps)
        # We'll show a 5-wide bar plus a dim background.
        value = max(0, min(10, value_0_to_10))
        filled = int(round(value / 2))
        dim = (max(10, color[0] // 5), max(10, color[1] // 5), max(10, color[2] // 5))
        for i in range(5):
            self.grid.set_pixel(x + i, y, dim)
        for i in range(filled):
            self.grid.set_pixel(x + i, y, color)

    def _render_dog(self, x: int, y: int, c: Color, a: Color):
        # Simple dog face
        # Ears
        self.grid.set_pixel(x + 0, y + 0, c)
        self.grid.set_pixel(x + 1, y + 1, c)
        self.grid.set_pixel(x + 8, y + 0, c)
        self.grid.set_pixel(x + 7, y + 1, c)
        # Head
        for dx in range(2, 7):
            self.grid.set_pixel(x + dx, y + 1, c)
        for dx in range(1, 8):
            self.grid.set_pixel(x + dx, y + 2, c)
            self.grid.set_pixel(x + dx, y + 3, c)
        # Eyes
        self.grid.set_pixel(x + 3, y + 2, (0, 0, 0))
        self.grid.set_pixel(x + 6, y + 2, (0, 0, 0))
        # Snout
        self.grid.set_pixel(x + 4, y + 4, a)
        self.grid.set_pixel(x + 5, y + 4, a)
        self.grid.set_pixel(x + 4, y + 5, a)
        self.grid.set_pixel(x + 5, y + 5, a)
        # Nose
        self.grid.set_pixel(x + 4, y + 4, (40, 40, 40))

    def _render_cat(self, x: int, y: int, c: Color, a: Color):
        # Cat head with pointy ears
        self.grid.set_pixel(x + 2, y + 0, c)
        self.grid.set_pixel(x + 6, y + 0, c)
        self.grid.set_pixel(x + 1, y + 1, c)
        self.grid.set_pixel(x + 7, y + 1, c)
        # Head block
        for dx in range(2, 7):
            self.grid.set_pixel(x + dx, y + 1, c)
        for dx in range(1, 8):
            self.grid.set_pixel(x + dx, y + 2, c)
            self.grid.set_pixel(x + dx, y + 3, c)
        # Eyes
        self.grid.set_pixel(x + 3, y + 2, (0, 0, 0))
        self.grid.set_pixel(x + 5, y + 2, (0, 0, 0))
        # Nose
        self.grid.set_pixel(x + 4, y + 3, a)
        # Whiskers
        self.grid.set_pixel(x + 0, y + 3, a)
        self.grid.set_pixel(x + 1, y + 3, a)
        self.grid.set_pixel(x + 7, y + 3, a)
        self.grid.set_pixel(x + 8, y + 3, a)

    def _render_dino(self, x: int, y: int, c: Color, a: Color):
        # Tiny dino profile: head + body + spikes
        # Spikes
        self.grid.set_pixel(x + 2, y + 0, a)
        self.grid.set_pixel(x + 3, y + 1, a)
        self.grid.set_pixel(x + 4, y + 0, a)
        # Head
        for dx in range(2, 7):
            self.grid.set_pixel(x + dx, y + 2, c)
        for dx in range(1, 7):
            self.grid.set_pixel(x + dx, y + 3, c)
        # Eye
        self.grid.set_pixel(x + 5, y + 2, (0, 0, 0))
        # Body
        for dx in range(2, 9):
            self.grid.set_pixel(x + dx, y + 4, c)
        for dx in range(3, 8):
            self.grid.set_pixel(x + dx, y + 5, c)
        # Tail
        self.grid.set_pixel(x + 9, y + 4, c)
        # Legs
        self.grid.set_pixel(x + 4, y + 6, c)
        self.grid.set_pixel(x + 6, y + 6, c)

    @staticmethod
    def _clamp_stat(v: float) -> float:
        return max(0.0, min(10.0, v))
