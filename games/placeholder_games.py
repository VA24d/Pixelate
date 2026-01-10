"""
Placeholder Games - Coming Soon screens
"""
from games.base_game import Game
import pygame


class PlaceholderGame(Game):
    """Base placeholder game with 'Coming Soon' message"""
    
    def __init__(self, grid, game_name: str, logo_render_func):
        super().__init__(grid)
        self.game_name = game_name
        self.logo_render_func = logo_render_func
        self.flash_timer = 0
    
    def update(self, dt: float):
        """Update placeholder animation"""
        self.flash_timer += dt
    
    def render(self):
        """Render coming soon screen"""
        self.grid.clear()
        
        # Render game logo
        self.logo_render_func(5, 3)
        
        # Flashing "COMING SOON" text
        flash = int(self.flash_timer * 2) % 2
        if flash:
            text_color = (255, 255, 0)
        else:
            text_color = (150, 150, 0)
        
        self.grid.render_text("SOON", 3, 14, text_color, scale=1)
    
    def handle_input(self, keys, events):
        """Handle input - ESC to return"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False


class SnakeGame(PlaceholderGame):
    """Snake placeholder"""
    
    def __init__(self, grid):
        super().__init__(grid, "SNAKE", self._render_logo)
    
    def _render_logo(self, x: int, y: int):
        """Render snake logo"""
        green = (0, 255, 0)
        lime = (150, 255, 0)
        red = (255, 0, 0)
        
        # Snake body in S shape
        snake_pixels = [
            (4, 0), (5, 0), (6, 0), (7, 0),
            (3, 1), (4, 1),
            (3, 2), (4, 2), (5, 2),
            (5, 3), (6, 3),
            (4, 4), (5, 4), (6, 4), (7, 4)
        ]
        
        for i, (dx, dy) in enumerate(snake_pixels):
            color = green if i % 2 == 0 else lime
            self.grid.set_pixel(x + dx, y + dy, color)
        
        # Apple (food)
        self.grid.set_pixel(x + 8, y + 1, red)
        self.grid.set_pixel(x + 9, y + 1, red)
        self.grid.set_pixel(x + 8, y + 2, red)
        self.grid.set_pixel(x + 9, y + 2, red)


class TetrisGame(PlaceholderGame):
    """Tetris placeholder"""
    
    def __init__(self, grid):
        super().__init__(grid, "TETRIS", self._render_logo)
    
    def _render_logo(self, x: int, y: int):
        """Render tetris logo with multiple pieces"""
        colors = [
            (255, 0, 0),      # Red - Z piece
            (0, 255, 0),      # Green - S piece
            (0, 0, 255),      # Blue - J piece
            (255, 255, 0),    # Yellow - O piece
            (255, 0, 255),    # Magenta - T piece
        ]
        
        # T-piece
        positions = [(4, 1), (5, 1), (6, 1), (5, 2)]
        for px, py in positions:
            self.grid.set_pixel(x + px, y + py, colors[4])
        
        # L-piece
        positions = [(3, 3), (3, 4), (3, 5), (4, 5)]
        for px, py in positions:
            self.grid.set_pixel(x + px, y + py, colors[2])
        
        # O-piece
        positions = [(6, 3), (7, 3), (6, 4), (7, 4)]
        for px, py in positions:
            self.grid.set_pixel(x + px, y + py, colors[3])
        
        # Z-piece
        positions = [(1, 4), (2, 4), (2, 5), (3, 5)]
        for px, py in positions:
            self.grid.set_pixel(x + px, y + py, colors[0])


class SpaceInvadersGame(PlaceholderGame):
    """Space Invaders placeholder"""
    
    def __init__(self, grid):
        super().__init__(grid, "SPACE", self._render_logo)
    
    def _render_logo(self, x: int, y: int):
        """Render space invaders logo"""
        cyan = (0, 255, 255)
        white = (255, 255, 255)
        
        # Classic space invader sprite
        alien = [
            [0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 0, 1, 1, 0, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
            [1, 0, 1, 0, 0, 0, 0, 1, 0, 1],
            [0, 0, 0, 1, 1, 1, 1, 0, 0, 0]
        ]
        
        for dy in range(len(alien)):
            for dx in range(len(alien[dy])):
                if alien[dy][dx]:
                    self.grid.set_pixel(x + dx, y + dy, cyan)
        
        # Player ship at bottom
        ship = [[0, 1, 0], [1, 1, 1]]
        for dy in range(len(ship)):
            for dx in range(len(ship[dy])):
                if ship[dy][dx]:
                    self.grid.set_pixel(x + dx + 3, y + dy + 9, white)
