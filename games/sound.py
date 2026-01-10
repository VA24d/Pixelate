"""Simple optional sound effects helper.

This project aims to be competition-demo friendly, so sound must be:
  - Optional (toggle on/off)
  - Safe if pygame.mixer fails to initialize
  - Lightweight (procedurally generated beeps; no external assets)
"""

from __future__ import annotations

import math
from typing import Dict, Tuple

import pygame


_enabled: bool = True
_initialized: bool = False
_available: bool = False

_cache: Dict[Tuple[int, int, float], pygame.mixer.Sound] = {}


def is_enabled() -> bool:
    return _enabled


def is_available() -> bool:
    return _available


def set_enabled(enabled: bool) -> None:
    global _enabled
    _enabled = bool(enabled)


def toggle_enabled() -> bool:
    """Toggle sound on/off. Returns new enabled state."""
    global _enabled
    _enabled = not _enabled
    return _enabled


def _ensure_init() -> None:
    """Attempt to initialize pygame mixer once."""
    global _initialized, _available
    if _initialized:
        return
    _initialized = True
    try:
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        _available = True
    except Exception:
        _available = False


def _get_beep(frequency: int, duration_ms: int, volume: float = 0.3) -> pygame.mixer.Sound | None:
    """Create/cached a beep sound buffer."""
    key = (frequency, duration_ms, float(volume))
    if key in _cache:
        return _cache[key]

    sample_rate = 22050
    duration = duration_ms / 1000.0
    n_samples = int(round(duration * sample_rate))
    if n_samples <= 0:
        return None

    # Signed 16-bit mono buffer
    sound_bytes = bytearray()
    amp = int(32767.0 * max(0.0, min(1.0, volume)))
    for i in range(n_samples):
        sample = int(amp * math.sin(2.0 * math.pi * float(frequency) * i / sample_rate))
        sound_bytes.extend(sample.to_bytes(2, byteorder="little", signed=True))

    snd = pygame.mixer.Sound(buffer=bytes(sound_bytes))
    _cache[key] = snd
    return snd


def play_beep(frequency: int, duration_ms: int = 50, volume: float = 0.3) -> None:
    """Play a beep if sound is enabled and available."""
    if not _enabled:
        return
    _ensure_init()
    if not _available:
        return

    try:
        snd = _get_beep(int(frequency), int(duration_ms), float(volume))
        if snd is not None:
            snd.play()
    except Exception:
        # Never let sound break gameplay.
        pass
