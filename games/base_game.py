"""
Base Game Class - Interface for all games
"""
from abc import ABC, abstractmethod
from typing import Tuple
import pygame


class Game(ABC):
    """Abstract base class for all games"""
    
    def __init__(self, grid):
        self.grid = grid
        self.running = True
    
    @abstractmethod
    def update(self, dt: float):
        """Update game state - called every frame"""
        pass
    
    @abstractmethod
    def render(self):
        """Render game to the LED grid"""
        pass
    
    @abstractmethod
    def handle_input(self, keys, events):
        """Handle keyboard input"""
        pass
    
    def is_running(self) -> bool:
        """Check if game is still running"""
        return self.running
    
    def exit(self):
        """Exit the game"""
        self.running = False


class GameState:
    """Enumeration of game states"""
    BOOT = "boot"
    MENU = "menu"
    PLAYING = "playing"
    EDITOR = "editor"


class GameManager:
    """Manages game state transitions and current game"""
    
    def __init__(self, grid):
        self.grid = grid
        self.state = GameState.BOOT
        self.current_game = None
        self.selected_game_index = 0
        
    def set_state(self, state: GameState):
        """Change the current game state"""
        self.state = state
    
    def start_game(self, game: Game):
        """Start a new game"""
        self.current_game = game
        self.state = GameState.PLAYING
    
    def return_to_menu(self):
        """Return from game to menu"""
        self.current_game = None
        self.state = GameState.MENU
    
    def update(self, dt: float):
        """Update current game or state"""
        if self.current_game and self.state == GameState.PLAYING:
            self.current_game.update(dt)
            if not self.current_game.is_running():
                self.return_to_menu()
    
    def render(self):
        """Render current game or state"""
        if self.current_game and self.state == GameState.PLAYING:
            self.current_game.render()
    
    def handle_input(self, keys, events):
        """Handle input for current game or state"""
        if self.current_game and self.state == GameState.PLAYING:
            self.current_game.handle_input(keys, events)


# Utility functions for drawing shapes and patterns
def draw_circle_pixels(grid, cx: int, cy: int, radius: int, color: Tuple[int, int, int]):
    """Draw a circle on the grid using pixel approximation"""
    for y in range(grid.grid_size):
        for x in range(grid.grid_size):
            dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if dist <= radius:
                grid.set_pixel(x, y, color)


def blend_colors(color1: Tuple[int, int, int], color2: Tuple[int, int, int], alpha: float) -> Tuple[int, int, int]:
    """Blend two colors with alpha (0.0 to 1.0)"""
    return (
        int(color1[0] * (1 - alpha) + color2[0] * alpha),
        int(color1[1] * (1 - alpha) + color2[1] * alpha),
        int(color1[2] * (1 - alpha) + color2[2] * alpha)
    )


def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
    """Convert HSV color to RGB (h: 0-360, s: 0-1, v: 0-1)"""
    import colorsys
    r, g, b = colorsys.hsv_to_rgb(h / 360.0, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))