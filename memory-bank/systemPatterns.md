# System Patterns

## Architecture Overview
```
main.py (LEDGameConsole)
├── led_grid.py (LEDGrid) - Rendering engine
└── games/
    ├── base_game.py (Game, GameManager) - Framework
    ├── boot_screen.py (BootScreen) - Startup animation
    ├── menu.py (CarouselMenu) - Game selection
    ├── pong.py (Pong) - Full game implementation
    ├── basketball.py (Basketball) - Full game implementation
    ├── snake.py (Snake) - Full game implementation
    ├── flappy.py (Flappy) - Full game implementation
    ├── vacation.py (VacationGallery) - Digital art gallery
    ├── pet_game.py (PetGame) - Pet sim
    ├── shadow_fight.py (ShadowFight) - Stick fighter
    └── asphalt_race.py (AsphaltRace) - Pseudo-3D racer
```

## Key Design Patterns

### Game Architecture
**Base Class Pattern**
```python
class Game(ABC):
    def update(dt: float)  # Game logic
    def render()           # Draw to grid
    def handle_input(keys, events)  # Process input
    def is_running() -> bool
```

All games inherit and implement these methods, ensuring consistent interface.

### State Management
**GameManager** handles transitions:
- `BOOT` → `MENU` → `PLAYING` → `MENU`
- Tracks current game and selected game index
- Manages state transitions cleanly

### LED Grid Abstraction
**LEDGrid** provides high-level API:
- `set_pixel(x, y, color)` - Individual LED control
- `render_text(text, x, y, color, scale)` - 3×5 bitmap font
- `render_number(num, x, y, color, scale)` - Numeric display
- `fill_rect()`, `draw_line()` - Shapes
- `clear(color)` - Full grid reset

### Rendering Pipeline
1. Game clears grid: `self.grid.clear()`
2. Game draws to grid: `self.grid.set_pixel()`, etc.
3. Grid renders to pygame surface with LED styling
4. Main loop updates display

## Critical Implementation Paths

### Boot → Menu → Game Flow
```python
# main.py
start_boot_screen()
  ↓ (boot finishes)
start_menu()
  ↓ (game selected)
start_game(index)
  ↓ (ESC pressed)
start_menu()
```

### AI Decision Making (Basketball)
```python
if has_ball:
    if close_to_hoop and not_blocked:
        shoot()
    elif opponent_close:
        pass_to_teammate()
    else:
        move_towards_hoop()
elif teammate_has_ball:
    position_for_pass()
elif opponent_has_ball:
    defend_and_attempt_steal()
else:
    chase_loose_ball()
```

### Input Handling
- **Global controls** (main.py): LED adjustments (+/-, [/], ,/., T, Q)
- **Game-specific controls** (each game): Game mechanics
- Events passed to current screen via `handle_input(keys, events)`

## Component Relationships

### LEDGrid ↔ Games
- Games modify grid state (logical)
- Grid handles rendering (visual)
- Separation of concerns: games don't know about pygame surfaces

### GameManager ↔ Main Loop
- Manager tracks state
- Main loop queries state and updates current screen
- Clean state transitions

### Sound System
- Procedural generation using pygame.mixer
- Beeps at different frequencies for different events
- Melody generation for victory/completion

## Important Constraints
- 19×19 grid size is fixed
- Grid coordinates: (0,0) top-left, (18,18) bottom-right
- Font is 3×5 pixels per character
- Colors are RGB tuples (0-255, 0-255, 0-255)
- Frame rate: 60 FPS
- No external image assets - all pixel art drawn programmatically