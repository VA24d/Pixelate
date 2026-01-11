"""Font store for user-editable 3x5 glyph overrides.

We keep this separate from SpriteStore because glyphs are not full-color sprites;
they are binary masks used by LEDGrid.render_text().

Persistence format (JSON):
  {
    "A": [[0,1,0],[1,0,1],[1,1,1],[1,0,1],[1,0,1]],
    "B": ...
  }

Only overrides are stored; any missing character falls back to the built-in font.
"""

from __future__ import annotations

import json
import os
from typing import Dict, List


Glyph = List[List[int]]  # 5 rows of 3 ints (0/1)
FontOverrides = Dict[str, Glyph]


def _coerce_glyph(raw) -> Glyph | None:
    try:
        rows = list(raw)
    except Exception:
        return None

    if len(rows) != 5:
        return None

    out: Glyph = []
    for row in rows:
        try:
            cols = list(row)
        except Exception:
            return None
        if len(cols) != 3:
            return None
        out.append([1 if int(v) else 0 for v in cols])
    return out


class FontStore:
    def __init__(self, path: str = "data/font_overrides.json"):
        self.path = path
        self._overrides: FontOverrides = {}

    def load(self) -> None:
        if not os.path.exists(self.path):
            self._overrides = {}
            return
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except Exception:
            self._overrides = {}
            return

        overrides: FontOverrides = {}
        for k, v in (raw or {}).items():
            try:
                ch = str(k).upper()
                glyph = _coerce_glyph(v)
                if glyph is None:
                    continue
                overrides[ch] = glyph
            except Exception:
                continue
        self._overrides = overrides

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._overrides, f, indent=2, sort_keys=True)

    def get_overrides(self) -> FontOverrides:
        return dict(self._overrides)

    def set_overrides(self, overrides: FontOverrides) -> None:
        self._overrides = dict(overrides)

    def set_glyph(self, ch: str, glyph: Glyph) -> None:
        ch = str(ch).upper()
        coerced = _coerce_glyph(glyph)
        if coerced is None:
            return
        self._overrides[ch] = coerced

    def clear_glyph(self, ch: str) -> None:
        self._overrides.pop(str(ch).upper(), None)

    def get_glyph(self, ch: str) -> Glyph | None:
        return self._overrides.get(str(ch).upper())


_default_store: FontStore | None = None


def get_font_store() -> FontStore:
    global _default_store
    if _default_store is None:
        _default_store = FontStore()
        _default_store.load()
    return _default_store
