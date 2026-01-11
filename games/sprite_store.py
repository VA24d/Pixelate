"""Sprite store for user-editable pixel art.

This provides a tiny persistence layer (JSON) so users can tweak menu logos and
game HUD icons live via an editor mode.

Sprite format:
  {
    "w": <int>,
    "h": <int>,
    "pixels": {"x,y": [r,g,b], ...}
  }
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Dict, Tuple


Color = Tuple[int, int, int]


@dataclass
class Sprite:
    w: int
    h: int
    pixels: Dict[Tuple[int, int], Color]

    def get(self, x: int, y: int) -> Color | None:
        return self.pixels.get((x, y))

    def set(self, x: int, y: int, color: Color | None) -> None:
        if not (0 <= x < self.w and 0 <= y < self.h):
            return
        if color is None:
            self.pixels.pop((x, y), None)
        else:
            self.pixels[(x, y)] = color


class SpriteStore:
    def __init__(self, path: str = "data/sprites.json"):
        self.path = path
        self._sprites: Dict[str, Sprite] = {}

    def load(self) -> None:
        if not os.path.exists(self.path):
            self._sprites = {}
            return
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except Exception:
            self._sprites = {}
            return

        sprites: Dict[str, Sprite] = {}
        for name, s in (raw or {}).items():
            try:
                w = int(s.get("w"))
                h = int(s.get("h"))
                pix = {}
                for k, v in (s.get("pixels") or {}).items():
                    xs, ys = k.split(",")
                    x, y = int(xs), int(ys)
                    r, g, b = v
                    pix[(x, y)] = (int(r), int(g), int(b))
                sprites[str(name)] = Sprite(w=w, h=h, pixels=pix)
            except Exception:
                continue
        self._sprites = sprites

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        raw = {}
        for name, sprite in self._sprites.items():
            pixels = {f"{x},{y}": [c[0], c[1], c[2]] for (x, y), c in sprite.pixels.items()}
            raw[name] = {"w": sprite.w, "h": sprite.h, "pixels": pixels}
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(raw, f, indent=2, sort_keys=True)

    def get_or_create(self, name: str, w: int, h: int) -> Sprite:
        sprite = self._sprites.get(name)
        if sprite is None or sprite.w != w or sprite.h != h:
            sprite = Sprite(w=w, h=h, pixels={})
            self._sprites[name] = sprite
        return sprite

    def get(self, name: str) -> Sprite | None:
        return self._sprites.get(name)


_default_store: SpriteStore | None = None


def get_sprite_store() -> SpriteStore:
    """Global store used by menu/games and editor."""
    global _default_store
    if _default_store is None:
        _default_store = SpriteStore()
        _default_store.load()
    return _default_store


def draw_sprite(grid, sprite: Sprite, ox: int, oy: int) -> None:
    for (x, y), c in sprite.pixels.items():
        grid.set_pixel(ox + x, oy + y, c)
