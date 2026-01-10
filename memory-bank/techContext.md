# Technical Context

## Technology Stack

### Core Dependencies
```
pygame >= 2.5.0  - Graphics, input, sound
numpy >= 1.24.0  - Array operations (not heavily used yet)
```

### Python Version
- Python 3.12 (via Anaconda base environment)
- Development on macOS

## Development Setup

### Project Structure
```
Pixelate/
├── main.py              - Application entry point
├── led_grid.py          - LED rendering engine
├── requirements.txt     - Dependencies
├── README.md           - User documentation
├── memory-bank/        - Project documentation
└── games/
    ├── __init__.py
    ├── base_game.py
    ├── boot_screen.py
    ├── menu.py
    ├── pong.py
    ├── basketball.py
    └── placeholder_games.py
```

### Running the Application
```bash
cd /Users/va/Pixelate
pip install -r requirements.txt
python main.py
```

### Exit Code History
- Initially: Exit 0 (success)
- After menu changes: Exit 0 (class order bug fixed)
- Current: Should be Exit 0

## Technical Constraints

### Grid Limitations
- Fixed 19×19 size
- RGB color space (8-bit per channel)
- No alpha/transparency
- Integer pixel coordinates

### Performance
- Target: 60 FPS
- Rendering: ~361 LEDs per frame (19×19)
- Each LED rendered as circle or square with glow effects
- No significant performance issues observed

### Input System
- Pygame event loop
- Key press detection for discrete actions
- Key state polling for continuous movement
- No mouse input (keyboard only)

### Sound System
- pygame.mixer at 22050 Hz
- Procedurally generated tones
- Frequencies: 220-880 Hz (musical notes)
- No external audio files

## Dependencies Deep Dive

### pygame
**Used for:**
- Window management (`pygame.display`)
- Surface rendering (`pygame.Surface`)
- Drawing primitives (`pygame.draw`)
- Event handling (`pygame.event`)
- Input state (`pygame.key`)
- Sound generation (`pygame.mixer`)
- Timing (`pygame.time`)

**Key modules:**
- `pygame.draw.circle()` - Circular LEDs
- `pygame.draw.rect()` - Square LEDs
- `pygame.mixer.Sound()` - Sound effects
- `pygame.time.Clock()` - Frame rate control

### numpy
**Currently minimal usage:**
- Available for future optimizations
- Could be used for grid operations if needed
- Not critical to current implementation

## Tool Usage Patterns

### Color Manipulation
```python
# HSV to RGB conversion for rainbow effects
from games.base_game import hsv_to_rgb
color = hsv_to_rgb(hue, saturation, value)

# Color blending
from games.base_game import blend_colors
result = blend_colors(color1, color2, alpha)
```

### Text Rendering
```python
# 3×5 bitmap font, supports: 0-9, A-Z, space, hyphen
grid.render_text("HELLO", x, y, color, scale=1)
grid.render_number(42, x, y, color, scale=2)
```

### Sound Generation
```python
# Generate beep at frequency for duration
sound = _generate_beep(440, 0.05)  # A4 note, 50ms
sound.play()
```

## Known Technical Debt
- No automated tests
- Hard-coded game list in menu and main
- Some magic numbers (speeds, delays) could be configurable
- Sound generation has try/catch wrapper (mixer sometimes fails on init)

## Development Environment
- Editor: VS Code with Copilot
- Terminal: zsh
- Package manager: pip (Anaconda environment)
- Version control: Not currently used (single developer, competition timeline)
