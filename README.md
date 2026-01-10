# LED Grid Game Console Simulator

A Python application simulating a 19×19 RGB LED grid with a game console interface featuring a boot screen, carousel menu, and games.

## Competition Features

- **19×19 RGB LED Grid Simulator** with runtime-adjustable parameters
- **Boot Screen** with animated LED effects
- **Carousel Menu** with 5 game options and pixel-art logos
- **Full Pong Game** with:
  - Player vs AI and 2-player modes
  - Multicolored ball trails
  - Scoring animations
  - Sound effects
  - Game over screen
- **Basketball** (2v2)
- **Pet Game** (Dog/Cat/Dino)
- **2 Placeholder Games** (Snake, Tetris)

## Installation

```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python main.py
```

## Controls

### Global Controls (anytime)
- `+/-` - Adjust LED size
- `[/]` - Adjust LED spacing
- `,/.` - Adjust LED gap
- `T` - Toggle circular/square LED style
- `L` - Toggle portrait/landscape window layout
- `O` - Toggle sound effects on/off
- `Q` - Quit application

### Boot Screen & Menu
- `LEFT/RIGHT` - Navigate between games
- `SPACE/ENTER` - Select game
- `M` - Toggle smooth/instant carousel transitions

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
│   ├── pong.py            # Full Pong implementation
│   ├── basketball.py      # Full Basketball implementation
│   ├── pet_game.py        # Pet Game (Dog/Cat/Dino)
│   └── placeholder_games.py # Snake, Tetris, Space Invaders placeholders
```

## Tips for Competition

- Start with circular LEDs for realistic effect, toggle to square for retro pixel look
- Adjust LED size/spacing to find the best visual balance for your display
- Use smooth carousel transitions for presentation, instant for quick navigation
- Demonstrate both 1P and 2P Pong modes to show versatility
- Let the boot screen play fully on first launch for impact

Good luck with your competition! 🎮✨
