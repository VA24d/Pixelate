"""
Boot Screen - Animated startup sequence
"""
import math
from games.base_game import Game, hsv_to_rgb


class BootScreen(Game):
    """Boot animation that plays on startup"""
    
    def __init__(self, grid):
        super().__init__(grid)
        self.timer = 0
        self.duration = 3.0  # 3 seconds boot animation
        self.animation_stage = 0
    
    def update(self, dt: float):
        """Update boot animation"""
        self.timer += dt
        
        # Auto-exit after duration
        if self.timer >= self.duration:
            self.running = False
    
    def render(self):
        """Render boot animation - scanning wave effect"""
        self.grid.clear()
        
        progress = self.timer / self.duration
        
        # Stage 1: Horizontal scanning lines (0-33%)
        if progress < 0.33:
            stage_progress = progress / 0.33
            num_lines = int(stage_progress * self.grid.grid_size)
            for i in range(num_lines):
                hue = (i * 20) % 360
                color = hsv_to_rgb(hue, 1.0, 1.0)
                for x in range(self.grid.grid_size):
                    self.grid.set_pixel(x, i, color)
        
        # Stage 2: Vertical scanning lines (33-66%)
        elif progress < 0.66:
            stage_progress = (progress - 0.33) / 0.33
            num_lines = int(stage_progress * self.grid.grid_size)
            for i in range(num_lines):
                hue = (i * 20) % 360
                color = hsv_to_rgb(hue, 1.0, 1.0)
                for y in range(self.grid.grid_size):
                    self.grid.set_pixel(i, y, color)
        
        # Stage 3: Circular wave from center (66-100%)
        else:
            stage_progress = (progress - 0.66) / 0.34
            center = self.grid.grid_size // 2
            max_radius = center * 1.5
            current_radius = stage_progress * max_radius
            
            for y in range(self.grid.grid_size):
                for x in range(self.grid.grid_size):
                    dist = math.sqrt((x - center) ** 2 + (y - center) ** 2)
                    
                    # Create a wave ring effect
                    if abs(dist - current_radius) < 3:
                        intensity = 1.0 - abs(dist - current_radius) / 3
                        hue = (dist * 10 + self.timer * 100) % 360
                        color = hsv_to_rgb(hue, 1.0, intensity)
                        self.grid.set_pixel(x, y, color)
    
    def handle_input(self, keys, events):
        """Handle input - allow skip with space or enter"""
        import pygame
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    self.running = False
