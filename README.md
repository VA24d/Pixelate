# Pixelate (19×19 LED Grid Game Console)

Pixelate is a **Python + pygame** app that simulates a **19×19 RGB LED matrix** with a retro game-console UI.

It includes a boot screen, a carousel menu, and a collection of small games designed to look good on an LED grid.


- Designed for the ERC Pixelate Event (Sadly didn't support dynamic content)
- Other components designed include(Look at Bhaskar's repo):
  - WebCam to stick figure
  - General purpose video to stick figure animation
  - Video to Grid functionality with improved contrast

## Games

Menu has 8 items:

1. Pong
2. Snake
3. Flappy
4. Basketball (2v2)
5. Pet Game
6. Vacation Gallery
7. Shadow Fight (Stick)
8. Asphalt Race (pseudo-3D)

## Installation

```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python main.py
```

## Customization (Pixel Editors)

Pixelate supports **live pixel editing** for menu logos, menu card pixels, and font glyphs.
Edits are stored locally and are **not committed**.

### 1) Edit a menu card (logo + text + any pixels you see)
- In the Menu, select a game and press **`E`**.
- Click a **palette color** (top row) to choose a color.
- **Left click** paints pixels, **right click** erases.
- Press **`S`** to save.
- Optional: press **`B`** to “bake” the current rendered card into the overlay, then tweak it.

### 2) Edit only the menu logo
- In the Menu, select a game and press **`Shift + E`**.

### 3) Edit the font (fix messy text)
- In the Menu, press **`F`**.
- Start in an atlas view; click a glyph to edit.
- In edit view you can toggle pixels and save overrides.

Files:
- `data/sprites.json` (menu logos + menu card overlays + HUD icons)
- `data/font_overrides.json` (3×5 glyph overrides)

## Controls

### Global Controls (anytime)
- `+/-` - Adjust LED size
- `[/]` - Adjust LED spacing
- `,/.` - Adjust LED gap
- `T` - Toggle circular/square LED style
- `L` - Toggle portrait/landscape window layout
- `O` - Toggle sound effects on/off
- `H` - Toggle help overlay
- `Q` - Quit application

### Boot Screen & Menu
- `LEFT/RIGHT` - Navigate between games
- `SPACE/ENTER` - Select game
- `M` - Toggle smooth/instant carousel transitions
- `E` - Edit selected game card pixels
- `Shift+E` - Edit selected game logo
- `F` - Edit font glyphs

### Snake
- Arrow keys - Move
- `SPACE` - Restart after game over
- `ESC` - Return to menu

Note: Snake wraps at edges (left/right, top/bottom).

### Flappy Bird
- `SPACE` - Flap
- `R` - Restart after game over
- `ESC` - Return to menu

### Shadow Fight (Stick)
- `A/D` - Move
- `W` - Jump
- `J` - Punch
- `S` - Crouch/Dodge
- `SPACE` - Restart after game over
- `ESC` - Return to menu

### Asphalt Racing
- `LEFT/RIGHT` - Steer
- `UP` - Accelerate
- `DOWN` - Brake
- `SPACE` - Restart after crash
- `ESC` - Return to menu

### Pong Game
- **Mode Selection**: `LEFT/RIGHT` to choose 1P or 2P, `SPACE/ENTER` to start
- **Player 1 (Left Paddle)**: `W/S`
- **Player 2 (Right Paddle, 2P mode only)**: `UP/DOWN`
- `ESC` - Return to menu

### Pet Game
- `LEFT/RIGHT` - Switch between Dog/Cat/Dino
- `A` - Feed
- `S` - Play
- `D` - Rest
- `ESC` - Return to menu

### Vacation Gallery
- `LEFT/RIGHT` - Switch between scenes
- `SPACE` - Toggle animation
- `ESC` - Return to menu

## Features to Demonstrate

1. **LED Grid Customization**: Show both circular and square LED styles with different sizes
2. **Carousel Transitions**: Toggle between smooth sliding and instant snap (press `M`)
3. **Pong Modes**: Demonstrate both 1-player (vs AI) and 2-player modes
4. **Animations**: Boot screen, scoring effects, multicolored ball trails
5. **Sound**: Paddle hits, wall bounces, scoring, victory melody

## Project Structure

```
Pixelate/
├── main.py                  # Main application entry point
├── led_grid.py             # LED grid renderer
├── requirements.txt        # Dependencies
├── games/
│   ├── base_game.py       # Base game class and utilities
│   ├── boot_screen.py     # Boot animation
│   ├── menu.py            # Carousel menu
│   ├── menu_card_editor.py# Edit full menu cards (pixels + text)
│   ├── pong.py            # Full Pong implementation
│   ├── basketball.py      # Full Basketball implementation
│   ├── pet_game.py        # Pet Game (Dog/Cat/Dino)
│   ├── vacation.py        # Vacation Gallery (Beach + Waterfall)
│   ├── sound.py           # Optional sound helper
│   ├── snake.py           # Snake
│   ├── flappy.py          # Flappy Bird
│   ├── shadow_fight.py    # Stick figure fighter
│   ├── asphalt_race.py    # Pseudo-3D racing
│   ├── font_editor.py      # Edit 3x5 font glyphs
│   ├── font_store.py       # Persist font overrides
│   └── ...
├── tests/                  # unittest suite
└── data/                   # local user presets (gitignored)
```

## Running Tests

```bash
python -m unittest discover -q
```
