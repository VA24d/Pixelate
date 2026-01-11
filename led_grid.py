"""
LED Grid Renderer - Simulates a 19x19 RGB LED matrix display
Supports runtime adjustment of LED size, spacing, and visual style
"""
import pygame
import math
from typing import Dict, Tuple, List


class LEDGrid:
    """Renders a 19x19 RGB LED grid with configurable display parameters"""
    
    def __init__(self, window_width: int = 1000, window_height: int = 1000):
        self.grid_size = 19
        self.window_width = window_width
        self.window_height = window_height
        
        # Configurable LED parameters (adjustable at runtime)
        self.led_size = 30  # Size of each LED in pixels
        self.led_spacing = 10  # Space between LEDs
        self.led_gap = 2  # Gap/border around each LED
        
        # Visual style
        self.circular_mode = True  # Toggle between circular and square LEDs
        
        # Grid data: 19x19 array of RGB colors
        self.grid = [[(0, 0, 0) for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # Calculate grid offset to center it
        self.update_grid_offset()

    def update_window_size(self, window_width: int, window_height: int):
        """Update the hosting window size (e.g., portrait/landscape toggle)."""
        self.window_width = window_width
        self.window_height = window_height
        self.update_grid_offset()
    
    def update_grid_offset(self):
        """Calculate offset to center the grid in the window"""
        total_size = (self.led_size + self.led_spacing) * self.grid_size - self.led_spacing
        self.offset_x = (self.window_width - total_size) // 2
        self.offset_y = (self.window_height - total_size) // 2
    
    def adjust_led_size(self, delta: int):
        """Adjust LED size (+ and - keys)"""
        self.led_size = max(5, min(60, self.led_size + delta))
        self.update_grid_offset()
    
    def adjust_led_spacing(self, delta: int):
        """Adjust spacing between LEDs ([ and ] keys)"""
        self.led_spacing = max(0, min(30, self.led_spacing + delta))
        self.update_grid_offset()
    
    def adjust_led_gap(self, delta: int):
        """Adjust gap/border around LEDs (, and . keys)"""
        self.led_gap = max(0, min(10, self.led_gap + delta))
    
    def toggle_style(self):
        """Toggle between circular and square LED style (T key)"""
        self.circular_mode = not self.circular_mode
    
    def set_pixel(self, x: int, y: int, color: Tuple[int, int, int]):
        """Set a single LED color (x, y coordinates, RGB color)"""
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            self.grid[y][x] = self._coerce_color(color)

    def _coerce_color(self, color) -> Tuple[int, int, int]:
        """Coerce arbitrary color-like input into an (r,g,b) tuple of ints 0..255.

        This is defensive: game logic should *ideally* only write integer RGB tuples,
        but we clamp here to prevent hard crashes during pygame drawing.
        """
        try:
            r, g, b = color  # type: ignore[misc]
        except Exception:
            return (0, 0, 0)

        def _clamp(v) -> int:
            try:
                vi = int(round(float(v)))
            except Exception:
                return 0
            return 0 if vi < 0 else 255 if vi > 255 else vi

        return (_clamp(r), _clamp(g), _clamp(b))
    
    def get_pixel(self, x: int, y: int) -> Tuple[int, int, int]:
        """Get a single LED color"""
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            return self.grid[y][x]
        return (0, 0, 0)
    
    def clear(self, color: Tuple[int, int, int] = (0, 0, 0)):
        """Clear the entire grid to a specific color (default black)"""
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                self.grid[y][x] = color
    
    def fill_rect(self, x: int, y: int, width: int, height: int, color: Tuple[int, int, int]):
        """Fill a rectangular area with a color"""
        for dy in range(height):
            for dx in range(width):
                self.set_pixel(x + dx, y + dy, color)
    
    def draw_line(self, x1: int, y1: int, x2: int, y2: int, color: Tuple[int, int, int]):
        """Draw a line between two points using Bresenham's algorithm"""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        x, y = x1, y1
        while True:
            self.set_pixel(x, y, color)
            if x == x2 and y == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
    
    def render(self, surface: pygame.Surface):
        """Render the LED grid to a pygame surface"""
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                color = self._coerce_color(self.grid[y][x])
                
                # Calculate LED position
                led_x = self.offset_x + x * (self.led_size + self.led_spacing)
                led_y = self.offset_y + y * (self.led_size + self.led_spacing)
                
                if self.circular_mode:
                    self._render_circular_led(surface, led_x, led_y, color)
                else:
                    self._render_square_led(surface, led_x, led_y, color)
    
    def _render_circular_led(self, surface: pygame.Surface, x: int, y: int, color: Tuple[int, int, int]):
        """Render a single circular LED with glow effect"""
        color = self._coerce_color(color)
        center_x = x + self.led_size // 2
        center_y = y + self.led_size // 2
        radius = (self.led_size - self.led_gap * 2) // 2
        
        # Draw dim background (off state visible)
        dim_color = (max(5, color[0] // 10), max(5, color[1] // 10), max(5, color[2] // 10))
        pygame.draw.circle(surface, dim_color, (center_x, center_y), radius + 1)
        
        # Draw main LED if not black
        if color != (0, 0, 0):
            # Outer glow
            glow_radius = radius + 2
            glow_color = (color[0] // 3, color[1] // 3, color[2] // 3)
            pygame.draw.circle(surface, glow_color, (center_x, center_y), glow_radius)
            
            # Main LED
            pygame.draw.circle(surface, color, (center_x, center_y), radius)
            
            # Highlight (top-left shine effect)
            highlight_color = (
                min(255, color[0] + 80),
                min(255, color[1] + 80),
                min(255, color[2] + 80)
            )
            highlight_radius = max(1, radius // 3)
            highlight_x = center_x - radius // 3
            highlight_y = center_y - radius // 3
            pygame.draw.circle(surface, highlight_color, (highlight_x, highlight_y), highlight_radius)
    
    def _render_square_led(self, surface: pygame.Surface, x: int, y: int, color: Tuple[int, int, int]):
        """Render a single square LED (pixel style)"""
        color = self._coerce_color(color)
        size = self.led_size - self.led_gap * 2
        
        # Draw dim background
        dim_color = (max(5, color[0] // 10), max(5, color[1] // 10), max(5, color[2] // 10))
        pygame.draw.rect(surface, dim_color, (x, y, self.led_size, self.led_size))
        
        # Draw main LED if not black
        if color != (0, 0, 0):
            pygame.draw.rect(surface, color, (x + self.led_gap, y + self.led_gap, size, size))
    
    def render_text(
        self,
        text: str,
        x: int,
        y: int,
        color: Tuple[int, int, int],
        scale: int = 1,
        spacing: int = 1,
    ):
        """Render text on the LED grid using a simple 3x5 font.

        Args:
            text: Text to render (A-Z, 0-9, space, hyphen).
            x,y: Top-left position.
            color: RGB tuple.
            scale: Pixel scale factor.
            spacing: Extra spacing between characters (in *unscaled* pixels).
        """
        font_3x5: Dict[str, List[List[int]]] = {
            '0': [[1,1,1],[1,0,1],[1,0,1],[1,0,1],[1,1,1]],
            '1': [[0,1,0],[1,1,0],[0,1,0],[0,1,0],[1,1,1]],
            '2': [[1,1,1],[0,0,1],[1,1,1],[1,0,0],[1,1,1]],
            '3': [[1,1,1],[0,0,1],[1,1,1],[0,0,1],[1,1,1]],
            '4': [[1,0,1],[1,0,1],[1,1,1],[0,0,1],[0,0,1]],
            '5': [[1,1,1],[1,0,0],[1,1,1],[0,0,1],[1,1,1]],
            '6': [[1,1,1],[1,0,0],[1,1,1],[1,0,1],[1,1,1]],
            '7': [[1,1,1],[0,0,1],[0,0,1],[0,0,1],[0,0,1]],
            '8': [[1,1,1],[1,0,1],[1,1,1],[1,0,1],[1,1,1]],
            '9': [[1,1,1],[1,0,1],[1,1,1],[0,0,1],[1,1,1]],
            'A': [[0,1,0],[1,0,1],[1,1,1],[1,0,1],[1,0,1]],
            'B': [[1,1,0],[1,0,1],[1,1,0],[1,0,1],[1,1,0]],
            'C': [[1,1,1],[1,0,0],[1,0,0],[1,0,0],[1,1,1]],
            'D': [[1,1,0],[1,0,1],[1,0,1],[1,0,1],[1,1,0]],
            'E': [[1,1,1],[1,0,0],[1,1,1],[1,0,0],[1,1,1]],
            'F': [[1,1,1],[1,0,0],[1,1,1],[1,0,0],[1,0,0]],
            'G': [[1,1,1],[1,0,0],[1,0,1],[1,0,1],[1,1,1]],
            'H': [[1,0,1],[1,0,1],[1,1,1],[1,0,1],[1,0,1]],
            'I': [[1,1,1],[0,1,0],[0,1,0],[0,1,0],[1,1,1]],
            'J': [[0,0,1],[0,0,1],[0,0,1],[1,0,1],[0,1,0]],
            'K': [[1,0,1],[1,1,0],[1,0,0],[1,1,0],[1,0,1]],
            'L': [[1,0,0],[1,0,0],[1,0,0],[1,0,0],[1,1,1]],
            'M': [[1,0,1],[1,1,1],[1,1,1],[1,0,1],[1,0,1]],
            'N': [[1,0,1],[1,1,1],[1,1,1],[1,0,1],[1,0,1]],
            'O': [[1,1,1],[1,0,1],[1,0,1],[1,0,1],[1,1,1]],
            'P': [[1,1,1],[1,0,1],[1,1,1],[1,0,0],[1,0,0]],
            'Q': [[1,1,1],[1,0,1],[1,0,1],[1,1,1],[0,0,1]],
            'R': [[1,1,1],[1,0,1],[1,1,1],[1,1,0],[1,0,1]],
            'S': [[1,1,1],[1,0,0],[1,1,1],[0,0,1],[1,1,1]],
            'T': [[1,1,1],[0,1,0],[0,1,0],[0,1,0],[0,1,0]],
            'U': [[1,0,1],[1,0,1],[1,0,1],[1,0,1],[1,1,1]],
            'V': [[1,0,1],[1,0,1],[1,0,1],[1,0,1],[0,1,0]],
            'W': [[1,0,1],[1,0,1],[1,1,1],[1,1,1],[1,0,1]],
            'X': [[1,0,1],[1,0,1],[0,1,0],[1,0,1],[1,0,1]],
            'Y': [[1,0,1],[1,0,1],[0,1,0],[0,1,0],[0,1,0]],
            'Z': [[1,1,1],[0,0,1],[0,1,0],[1,0,0],[1,1,1]],
            ' ': [[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]],
            '-': [[0,0,0],[0,0,0],[1,1,1],[0,0,0],[0,0,0]],
        }

        # Apply optional user overrides loaded at runtime.
        # Overrides should follow the same 3x5 matrix format.
        try:
            font_3x5.update(self._font_overrides)
        except Exception:
            pass
        
        cursor_x = x
        for char in text.upper():
            if char in font_3x5:
                pattern = font_3x5[char]
                for dy in range(5):
                    for dx in range(3):
                        if pattern[dy][dx]:
                            for sy in range(scale):
                                for sx in range(scale):
                                    self.set_pixel(cursor_x + dx * scale + sx, y + dy * scale + sy, color)
                cursor_x += (3 * scale) + (max(0, int(spacing)) * scale)  # Character width + spacing

    def set_font_overrides(self, overrides: Dict[str, List[List[int]]] | None) -> None:
        """Set per-character 3x5 font overrides used by render_text()."""
        self._font_overrides = overrides or {}

    def get_font_overrides(self) -> Dict[str, List[List[int]]]:
        return getattr(self, "_font_overrides", {})
    
    def render_number(self, number: int, x: int, y: int, color: Tuple[int, int, int], scale: int = 1):
        """Render a number on the LED grid"""
        self.render_text(str(number), x, y, color, scale)