"""Simple text layout helpers to avoid overlapping / 'messed up' text.

On a 19x19 grid, text must be constrained to small zones.
We provide standard zones so screens can be consistent:

  - TITLE: top row area
  - HUD_LEFT / HUD_RIGHT: top-left / top-right blocks
  - HINT: bottom row area

This is deliberately minimal so existing games don't need major refactors.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TextZone:
    x: int
    y: int
    w: int
    h: int


TITLE = TextZone(x=0, y=0, w=19, h=5)
HINT = TextZone(x=0, y=14, w=19, h=5)

HUD_LEFT = TextZone(x=0, y=0, w=9, h=7)
HUD_RIGHT = TextZone(x=10, y=0, w=9, h=7)


def text_width(chars: int, scale: int = 1, spacing: int = 1) -> int:
    # 3 wide + spacing per char. spacing is unscaled.
    return chars * ((3 + spacing) * scale)


def centered_x(zone: TextZone, chars: int, scale: int = 1, spacing: int = 1) -> int:
    w = text_width(chars=chars, scale=scale, spacing=spacing)
    return zone.x + max(0, (zone.w - w) // 2)
