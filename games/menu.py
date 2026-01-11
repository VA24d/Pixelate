"""
Carousel Menu - Game selection with pixel art logos
"""
import pygame
import math

from games.base_game import Game, hsv_to_rgb
from games.sound import play_beep
from games.sprite_store import get_sprite_store, draw_sprite
from games.text_layout import TITLE, HINT, centered_x


class CarouselMenu(Game):
    """Horizontal carousel menu for game selection"""
    
    def __init__(self, grid, game_manager):
        super().__init__(grid)
        self.game_manager = game_manager
        self.selected_index = 0
        self.num_games = 8

        # Each card is rendered on the 19x19 grid; we slide cards horizontally by this width.
        self.card_width = self.grid.grid_size
        
        # Animation settings
        self.smooth_transition = True  # Toggle with 'M' key
        self.target_index = 0
        self.current_offset = 0.0  # For smooth scrolling
        self.scroll_speed = 8.0

        # UI polish
        self.title_pulse = 0.0
        
        # Game information
        self._sprite_store = get_sprite_store()
        self.games = [
            {"name": "PONG", "number": 1},
            {"name": "SNAKE", "number": 2},
            {"name": "FLAP", "number": 3},
            {"name": "BBALL", "number": 4},
            {"name": "PETS", "number": 5},
            {"name": "VACAY", "number": 6},
            {"name": "FIGHT", "number": 7},
            {"name": "RACE", "number": 8},
        ]
    
    def update(self, dt: float):
        """Update menu animation"""
        self.title_pulse += dt
        if self.smooth_transition:
            # Smooth scrolling animation
            target_offset = self.target_index
            diff = target_offset - self.current_offset
            if abs(diff) > 0.01:
                self.current_offset += diff * self.scroll_speed * dt
            else:
                self.current_offset = target_offset
    
    def render(self):
        """Render carousel menu"""
        # Slightly tinted background for better depth
        self.grid.clear((0, 0, 8))

        # Top title bar (subtle)
        pulse = (math.sin(self.title_pulse * 2.0) + 1.0) / 2.0
        title_color = (
            int(60 + 80 * pulse),
            int(180 + 40 * pulse),
            int(255),
        )
        self.grid.render_text("GAMES", centered_x(TITLE, chars=5), TITLE.y, title_color, scale=1)
        
        # Calculate which games to show
        if self.smooth_transition:
            display_offset = self.current_offset
        else:
            display_offset = self.selected_index
        
        if self.smooth_transition:
            # Render nearby cards with horizontal sliding.
            # (Cards draw off-grid safely; LEDGrid.set_pixel bounds-checks.)
            for i in range(self.num_games):
                if abs(i - display_offset) <= 1.25:
                    self._render_game_card(i, display_offset)
        else:
            # Instant mode (snap) + simple adjacent previews.
            self._render_game_card(self.selected_index, display_offset)

            # Render left preview
            if self.selected_index > 0:
                self._render_game_preview(self.selected_index - 1, -1)

            # Render right preview
            if self.selected_index < self.num_games - 1:
                self._render_game_preview(self.selected_index + 1, 1)

        # Left/right arrows (only show if navigation is possible)
        arrow_color = (130, 130, 130)
        if self.selected_index > 0:
            self._render_left_arrow(1, 9, arrow_color)
        if self.selected_index < self.num_games - 1:
            self._render_right_arrow(17, 9, arrow_color)

        # Bottom hint
        hint = "LR SEL"
        self.grid.render_text(
            hint,
            centered_x(HINT, chars=len(hint)),
            HINT.y,
            (120, 120, 120),
            scale=1,
        )
    
    def _render_game_card(self, game_index: int, offset: float):
        """Render the main game card in center"""
        if game_index < 0 or game_index >= len(self.games):
            return
        
        game = self.games[game_index]
        
        # Horizontal slide (in LED pixels)
        # When offset == game_index => x_shift == 0 (card centered)
        x_shift = int((game_index - offset) * self.card_width)
        
        # Card border (helps readability during slide)
        border_color = (30, 30, 40)
        for bx in range(0, self.grid.grid_size):
            self.grid.set_pixel(x_shift + bx, 4, border_color)
            self.grid.set_pixel(x_shift + bx, 18, border_color)
        for by in range(4, 19):
            self.grid.set_pixel(x_shift + 0, by, border_color)
            self.grid.set_pixel(x_shift + 18, by, border_color)

        # Render game number at top
        number_y = 2
        self.grid.render_number(game["number"], x_shift + 8, number_y, (255, 255, 0), scale=1)
        
        # Render pixel art logo for the game
        logo_y = 6
        self._render_logo(game_index, x_shift + 4, logo_y)
        
        # Render game name at bottom
        name = game["name"]
        # Calculate text position to center it
        text_width = len(name) * 4  # 3 chars + 1 spacing per letter
        text_x = x_shift + (self.grid.grid_size - text_width) // 2
        self.grid.render_text(name, text_x, 15, (0, 255, 255), scale=1)
    
    def _render_game_preview(self, game_index: int, position: int):
        """Render a small preview of adjacent games (dimmed)"""
        # For simplicity, just show the game number on the edge
        if game_index < 0 or game_index >= len(self.games):
            return
        
        game = self.games[game_index]
        
        # Show preview number on the appropriate edge
        if position < 0:  # Left preview
            preview_x = 1
        else:  # Right preview
            preview_x = 15
        
        preview_y = self.grid.grid_size // 2 - 2
        dim_color = (80, 80, 80)
        self.grid.render_number(game["number"], preview_x, preview_y, dim_color, scale=1)
    
    def _render_logo(self, game_index: int, x: int, y: int):
        """Render pixel art logo for each game"""
        # Allow user overrides via sprite store.
        try:
            name = self.games[game_index]["name"]
            sprite = self._sprite_store.get(f"menu_logo_{name}")
            if sprite is not None:
                draw_sprite(self.grid, sprite, x, y)
                return
        except Exception:
            pass

        if game_index == 0:  # PONG
            self._render_pong_logo(x, y)
        elif game_index == 1:  # SNAKE
            self._render_snake_logo(x, y)
        elif game_index == 2:  # FLAPPY
            self._render_flappy_logo(x, y)
        elif game_index == 3:  # BBALL
            self._render_basketball_logo(x, y)
        elif game_index == 4:  # PETS
            self._render_pet_logo(x, y)
        elif game_index == 5:  # VACAY
            self._render_vacay_logo(x, y)
        elif game_index == 6:  # FIGHT
            self._render_fight_logo(x, y)
        elif game_index == 7:  # RACE
            self._render_race_logo(x, y)
    
    def _render_pong_logo(self, x: int, y: int):
        """Pixel art logo for Pong - paddles and ball"""
        white = (255, 255, 255)
        yellow = (255, 255, 0)
        
        # Left paddle
        for i in range(5):
            self.grid.set_pixel(x, y + i + 1, white)
            self.grid.set_pixel(x + 1, y + i + 1, white)
        
        # Right paddle
        for i in range(5):
            self.grid.set_pixel(x + 9, y + i + 1, white)
            self.grid.set_pixel(x + 10, y + i + 1, white)
        
        # Ball in center
        self.grid.set_pixel(x + 5, y + 3, yellow)
        self.grid.set_pixel(x + 5, y + 4, yellow)
        self.grid.set_pixel(x + 6, y + 3, yellow)
        self.grid.set_pixel(x + 6, y + 4, yellow)
    
    def _render_snake_logo(self, x: int, y: int):
        """Pixel art logo for Snake - snake shape"""
        green = (0, 255, 0)
        lime = (150, 255, 0)
        
        # Snake body in S shape
        snake_pixels = [
            (5, 1), (6, 1), (7, 1),
            (4, 2), (5, 2),
            (4, 3), (5, 3), (6, 3),
            (6, 4), (7, 4),
            (5, 5), (6, 5), (7, 5)
        ]
        
        for i, (dx, dy) in enumerate(snake_pixels):
            color = green if i % 2 == 0 else lime
            self.grid.set_pixel(x + dx, y + dy, color)
    
    def _render_flappy_logo(self, x: int, y: int):
        """Pixel art logo for Flappy - bird + pipe."""
        bird = (255, 230, 60)
        pipe = (0, 200, 80)

        # Pipe column
        for dy in range(0, 8):
            if dy in (3, 4):
                continue
            self.grid.set_pixel(x + 8, y + dy, pipe)
            self.grid.set_pixel(x + 9, y + dy, (0, 150, 60))

        # Bird
        self.grid.set_pixel(x + 3, y + 3, bird)
        self.grid.set_pixel(x + 3, y + 4, bird)
        self.grid.set_pixel(x + 4, y + 3, (255, 180, 0))
        self.grid.set_pixel(x + 4, y + 4, (255, 180, 0))
    
    def _render_basketball_logo(self, x: int, y: int):
        """Pixel art logo for Basketball - Miami Heat style"""
        # Colors for Miami Heat logo
        red = (200, 30, 45)  # Heat red
        maroon = (150, 20, 35)
        black = (20, 20, 20)
        orange = (255, 100, 0)
        white = (255, 255, 255)
        
        # Basketball hoop/ring (top)
        ring = [
            [0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        ]
        for dy in range(len(ring)):
            for dx in range(len(ring[dy])):
                if ring[dy][dx]:
                    self.grid.set_pixel(x + dx, y + dy, black)
        
        # Flame/heat shape (red basketball-like shape)
        flame = [
            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 1, 2, 2, 1, 0, 0, 0],
            [0, 0, 1, 2, 2, 2, 2, 1, 0, 0],
            [0, 1, 2, 2, 2, 2, 2, 2, 1, 0],
            [0, 1, 2, 2, 2, 2, 2, 2, 1, 0],
            [0, 0, 1, 2, 2, 2, 2, 1, 0, 0],
            [0, 0, 0, 1, 2, 2, 1, 0, 0, 0]
        ]
        for dy in range(len(flame)):
            for dx in range(len(flame[dy])):
                if flame[dy][dx] == 1:
                    self.grid.set_pixel(x + dx, y + dy + 1, maroon)
                elif flame[dy][dx] == 2:
                    self.grid.set_pixel(x + dx, y + dy + 1, red)

    def _render_pet_logo(self, x: int, y: int):
        """Pixel art logo for Pets - simple pawprint"""
        pink = (255, 120, 180)
        dark = (180, 60, 120)

        # Toe beans
        toes = [(2, 1), (4, 0), (6, 0), (8, 1)]
        for tx, ty in toes:
            self.grid.set_pixel(x + tx, y + ty, pink)
            self.grid.set_pixel(x + tx, y + ty + 1, dark)

        # Paw pad
        pad = [
            (4, 3), (5, 3), (6, 3),
            (3, 4), (4, 4), (5, 4), (6, 4), (7, 4),
            (3, 5), (4, 5), (5, 5), (6, 5), (7, 5),
            (4, 6), (5, 6), (6, 6),
        ]
        for i, (px, py) in enumerate(pad):
            self.grid.set_pixel(x + px, y + py, pink if i % 2 == 0 else dark)

    def _render_vacay_logo(self, x: int, y: int):
        """Pixel art logo for Vacation - small sun + waves."""
        sun = (255, 220, 80)
        sky = (80, 160, 255)
        wave = (120, 220, 255)
        sand = (200, 160, 80)

        # sky strip
        for dx in range(10):
            self.grid.set_pixel(x + dx, y + 0, sky)

        # sun
        self.grid.set_pixel(x + 7, y + 1, sun)
        self.grid.set_pixel(x + 6, y + 1, sun)
        self.grid.set_pixel(x + 7, y + 2, sun)

        # waves
        for dx in range(10):
            if dx % 2 == 0:
                self.grid.set_pixel(x + dx, y + 3, wave)
        for dx in range(10):
            self.grid.set_pixel(x + dx, y + 4, (0, 120, 200))

        # sand
        for dx in range(10):
            self.grid.set_pixel(x + dx, y + 5, sand)

    def _render_fight_logo(self, x: int, y: int):
        """Pixel art logo for Fight - two stick heads facing each other."""
        left = (255, 255, 255)
        right = (30, 30, 30)
        mid = (255, 255, 0)
        # heads
        self.grid.set_pixel(x + 2, y + 2, left)
        self.grid.set_pixel(x + 7, y + 2, right)
        # bodies
        self.grid.set_pixel(x + 2, y + 4, left)
        self.grid.set_pixel(x + 7, y + 4, right)
        # VS
        self.grid.set_pixel(x + 4, y + 3, mid)
        self.grid.set_pixel(x + 5, y + 3, mid)

    def _render_race_logo(self, x: int, y: int):
        """Pixel art logo for Race - small road + car."""
        road = (80, 80, 80)
        edge = (220, 220, 220)
        car1 = (60, 200, 255)

        # road taper
        for dy in range(0, 8):
            hw = 1 + dy // 2
            cy = y + dy
            cx = x + 5
            for dx in range(-hw, hw + 1):
                self.grid.set_pixel(cx + dx, cy, road)
            self.grid.set_pixel(cx - hw, cy, edge)
            self.grid.set_pixel(cx + hw, cy, edge)

        # car
        self.grid.set_pixel(x + 4, y + 6, car1)
        self.grid.set_pixel(x + 5, y + 6, (20, 120, 200))
        self.grid.set_pixel(x + 4, y + 7, (20, 120, 200))
        self.grid.set_pixel(x + 5, y + 7, car1)
    
    def handle_input(self, keys, events):
        """Handle carousel navigation"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    play_beep(420, 35)
                    self._move_selection(-1)
                elif event.key == pygame.K_RIGHT:
                    play_beep(520, 35)
                    self._move_selection(1)
                elif event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    play_beep(740, 60)
                    self._select_game()
                elif event.key == pygame.K_m:
                    # Toggle smooth/instant transition mode
                    self.smooth_transition = not self.smooth_transition
                    play_beep(660, 40)
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

    def _render_left_arrow(self, x: int, y: int, color: tuple[int, int, int]):
        """Render a small '<' arrow centered at (x,y)."""
        pts = [(0, 0), (1, -1), (1, 1), (2, -2), (2, 2)]
        for dx, dy in pts:
            self.grid.set_pixel(x + dx, y + dy, color)

    def _render_right_arrow(self, x: int, y: int, color: tuple[int, int, int]):
        """Render a small '>' arrow centered at (x,y)."""
        pts = [(0, 0), (-1, -1), (-1, 1), (-2, -2), (-2, 2)]
        for dx, dy in pts:
            self.grid.set_pixel(x + dx, y + dy, color)
    
    def _move_selection(self, direction: int):
        """Move selection left or right"""
        self.selected_index = max(0, min(self.num_games - 1, self.selected_index + direction))
        self.target_index = self.selected_index
        
        if not self.smooth_transition:
            self.current_offset = self.target_index
    
    def _select_game(self):
        """Launch the selected game"""
        self.game_manager.selected_game_index = self.selected_index
        self.running = False