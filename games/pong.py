"""
Pong Game - Full implementation with animations, scoring, and sound
"""
import pygame
import random
import math
from games.base_game import Game, hsv_to_rgb


class Pong(Game):
    """Classic Pong game with advanced features"""
    
    def __init__(self, grid):
        super().__init__(grid)
        
        # Game mode selection
        self.mode_selected = False
        # 0 = vs AI, 1 = 2P
        self.mode_index = 0
        self.two_player_mode = False  # Derived from mode_index when starting
        
        # Paddle settings
        self.paddle_height = 4
        self.paddle_speed = 12.0
        self.left_paddle_y = (self.grid.grid_size - self.paddle_height) // 2
        self.right_paddle_y = (self.grid.grid_size - self.paddle_height) // 2
        
        # Ball settings
        self.ball_x = self.grid.grid_size / 2
        self.ball_y = self.grid.grid_size / 2
        self.ball_vx = 0
        self.ball_vy = 0
        self.ball_speed = 8.0
        self.ball_trail = []  # For multicolored trail effect
        self.max_trail_length = 5
        
        # Scoring
        self.left_score = 0
        self.right_score = 0
        self.max_score = 5
        self.score_animation_timer = 0
        self.scoring_player = None  # 'left' or 'right'
        
        # Game state
        self.game_started = False
        self.game_over = False
        self.winner = None
        
        # AI settings
        self.ai_reaction_delay = 0.05
        self.ai_timer = 0
        self.ai_speed = 0.8  # AI paddle speed multiplier
        
        # Sound setup
        self.setup_sounds()
    
    def setup_sounds(self):
        """Initialize pygame mixer and create sound effects"""
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            
            # Generate simple beep sounds
            self.sound_paddle = self._generate_beep(440, 0.05)  # A4 note
            self.sound_wall = self._generate_beep(330, 0.05)    # E4 note
            self.sound_score = self._generate_beep(220, 0.2)    # A3 note
            self.sound_win = self._generate_melody()
        except:
            # Sound disabled if mixer fails
            self.sound_paddle = None
            self.sound_wall = None
            self.sound_score = None
            self.sound_win = None
    
    def _generate_beep(self, frequency: float, duration: float) -> pygame.mixer.Sound:
        """Generate a simple beep sound"""
        sample_rate = 22050
        n_samples = int(round(duration * sample_rate))
        buf = [int(32767.0 * 0.3 * math.sin(2.0 * math.pi * frequency * i / sample_rate)) 
               for i in range(n_samples)]
        
        # Convert to bytes
        sound_bytes = bytearray()
        for sample in buf:
            sound_bytes.extend(sample.to_bytes(2, byteorder='little', signed=True))
        
        return pygame.mixer.Sound(buffer=bytes(sound_bytes))
    
    def _generate_melody(self) -> pygame.mixer.Sound:
        """Generate a victory melody"""
        sample_rate = 22050
        notes = [440, 554, 659, 880]  # A, C#, E, A (major chord)
        duration = 0.15
        
        all_samples = []
        for freq in notes:
            n_samples = int(round(duration * sample_rate))
            samples = [int(32767.0 * 0.3 * math.sin(2.0 * math.pi * freq * i / sample_rate)) 
                      for i in range(n_samples)]
            all_samples.extend(samples)
        
        sound_bytes = bytearray()
        for sample in all_samples:
            sound_bytes.extend(sample.to_bytes(2, byteorder='little', signed=True))
        
        return pygame.mixer.Sound(buffer=bytes(sound_bytes))
    
    def _play_sound(self, sound):
        """Play a sound if available"""
        if sound:
            try:
                sound.play()
            except:
                pass
    
    def reset_ball(self):
        """Reset ball to center with random direction"""
        self.ball_x = self.grid.grid_size / 2
        self.ball_y = self.grid.grid_size / 2
        
        # Random angle between -45 and 45 degrees, randomly left or right
        angle = random.uniform(-math.pi/4, math.pi/4)
        direction = random.choice([-1, 1])
        
        self.ball_vx = math.cos(angle) * self.ball_speed * direction
        self.ball_vy = math.sin(angle) * self.ball_speed
        self.ball_trail.clear()
    
    def update(self, dt: float):
        """Update game state"""
        # Mode selection screen
        if not self.mode_selected:
            return
        
        # Score animation
        if self.score_animation_timer > 0:
            self.score_animation_timer -= dt
            if self.score_animation_timer <= 0:
                self.scoring_player = None
                if not self.game_over:
                    self.reset_ball()
                    self.game_started = True
            return
        
        # Game over state
        if self.game_over:
            return
        
        # Start the ball on first input
        if not self.game_started:
            return
        
        # Update ball position
        self.ball_x += self.ball_vx * dt
        self.ball_y += self.ball_vy * dt
        
        # Add to trail
        self.ball_trail.append((int(self.ball_x), int(self.ball_y)))
        if len(self.ball_trail) > self.max_trail_length:
            self.ball_trail.pop(0)
        
        # Ball collision with top/bottom walls
        if self.ball_y <= 0 or self.ball_y >= self.grid.grid_size - 1:
            self.ball_vy *= -1
            self.ball_y = max(0, min(self.grid.grid_size - 1, self.ball_y))
            self._play_sound(self.sound_wall)
        
        # Ball collision with paddles
        ball_x_int = int(self.ball_x)
        ball_y_int = int(self.ball_y)
        
        # Left paddle collision
        if ball_x_int <= 1 and self.left_paddle_y <= ball_y_int < self.left_paddle_y + self.paddle_height:
            self.ball_vx = abs(self.ball_vx)
            self.ball_x = 2
            self._add_spin(ball_y_int, self.left_paddle_y)
            self._play_sound(self.sound_paddle)
        
        # Right paddle collision
        if ball_x_int >= self.grid.grid_size - 2 and self.right_paddle_y <= ball_y_int < self.right_paddle_y + self.paddle_height:
            self.ball_vx = -abs(self.ball_vx)
            self.ball_x = self.grid.grid_size - 3
            self._add_spin(ball_y_int, self.right_paddle_y)
            self._play_sound(self.sound_paddle)
        
        # Scoring
        if self.ball_x < 0:
            self.right_score += 1
            self.scoring_player = 'right'
            self.score_animation_timer = 1.5
            self.game_started = False
            self._play_sound(self.sound_score)
            
            if self.right_score >= self.max_score:
                self.game_over = True
                self.winner = 'right'
                self._play_sound(self.sound_win)
        
        elif self.ball_x >= self.grid.grid_size:
            self.left_score += 1
            self.scoring_player = 'left'
            self.score_animation_timer = 1.5
            self.game_started = False
            self._play_sound(self.sound_score)
            
            if self.left_score >= self.max_score:
                self.game_over = True
                self.winner = 'left'
                self._play_sound(self.sound_win)
        
        # AI opponent logic - update every frame for smooth movement
        # (Only when game is actually running and not in a paused/animation state)
        if (not self.two_player_mode
            and self.mode_selected
            and self.game_started
            and not self.game_over
            and self.score_animation_timer <= 0):
            self._update_ai(dt)
    
    def _add_spin(self, ball_y: int, paddle_y: int):
        """Add spin to ball based on where it hit the paddle"""
        hit_pos = (ball_y - paddle_y) / self.paddle_height  # 0 to 1
        hit_offset = hit_pos - 0.5  # -0.5 to 0.5
        
        # Adjust vertical velocity based on hit position
        self.ball_vy += hit_offset * self.ball_speed * 0.5
        
        # Limit vertical speed
        max_vy = self.ball_speed * 0.8
        self.ball_vy = max(-max_vy, min(max_vy, self.ball_vy))
    
    def _update_ai(self, dt: float):
        """Simple AI for right paddle (dt-based so it works at any FPS)"""
        # Target the ball's Y position
        target_y = self.ball_y - self.paddle_height / 2

        # Add some imperfection
        target_y += random.uniform(-0.3, 0.3)

        # Smooth movement towards target
        diff = target_y - self.right_paddle_y

        # Interpret ai_speed as a per-second speed multiplier, not per-frame pixels.
        # This avoids "AI doesn't move" on systems where dt makes updates tiny.
        move_amount = max(0.0, self.paddle_speed * self.ai_speed * dt)

        if abs(diff) > 0.25:
            if diff > 0:
                self.right_paddle_y = min(
                    self.grid.grid_size - self.paddle_height,
                    self.right_paddle_y + move_amount,
                )
            else:
                self.right_paddle_y = max(0, self.right_paddle_y - move_amount)
    
    def render(self):
        """Render the game"""
        self.grid.clear()
        
        # Mode selection screen
        if not self.mode_selected:
            self._render_mode_selection()
            return
        
        # Score animation
        if self.score_animation_timer > 0:
            self._render_score_animation()
            return
        
        # Game over screen
        if self.game_over:
            self._render_game_over()
            return
        
        # Render paddles
        self._render_paddle(0, int(self.left_paddle_y), (0, 255, 255))
        self._render_paddle(self.grid.grid_size - 1, int(self.right_paddle_y), (255, 0, 255))
        
        # Render ball trail (multicolored)
        for i, (tx, ty) in enumerate(self.ball_trail):
            intensity = (i + 1) / len(self.ball_trail)
            hue = (pygame.time.get_ticks() / 10 + i * 30) % 360
            color = hsv_to_rgb(hue, 1.0, intensity * 0.6)
            if 0 <= tx < self.grid.grid_size and 0 <= ty < self.grid.grid_size:
                self.grid.set_pixel(tx, ty, color)
        
        # Render ball
        ball_x_int = int(self.ball_x)
        ball_y_int = int(self.ball_y)
        if 0 <= ball_x_int < self.grid.grid_size and 0 <= ball_y_int < self.grid.grid_size:
            self.grid.set_pixel(ball_x_int, ball_y_int, (255, 255, 255))
        
        # Render scores
        self.grid.render_number(self.left_score, 3, 1, (0, 255, 255), scale=1)
        self.grid.render_number(self.right_score, 13, 1, (255, 0, 255), scale=1)
        
        # Center line
        for y in range(0, self.grid.grid_size, 2):
            self.grid.set_pixel(self.grid.grid_size // 2, y, (50, 50, 50))
    
    def _render_paddle(self, x: int, y: int, color: tuple):
        """Render a paddle"""
        for i in range(self.paddle_height):
            py = y + i
            if 0 <= py < self.grid.grid_size:
                self.grid.set_pixel(x, py, color)
    
    def _render_mode_selection(self):
        """Render mode selection screen"""
        self.grid.render_text("MODE", 4, 2, (255, 255, 0), scale=1)
        
        # 1 Player option
        color1 = (0, 255, 0) if self.mode_index == 0 else (100, 100, 100)
        self.grid.render_text("1P", 3, 8, color1, scale=1)
        
        # 2 Player option
        color2 = (0, 255, 0) if self.mode_index == 1 else (100, 100, 100)
        self.grid.render_text("2P", 11, 8, color2, scale=1)
        
        # Instructions
        self.grid.render_text("LR", 5, 14, (150, 150, 150), scale=1)
    
    def _render_score_animation(self):
        """Render scoring animation with color effects"""
        flash = int(self.score_animation_timer * 10) % 2
        
        if self.scoring_player == 'left':
            color = (0, 255, 255) if flash else (0, 150, 150)
            # Fill left side with color pulse
            for x in range(self.grid.grid_size // 2):
                for y in range(self.grid.grid_size):
                    intensity = 1.0 - (x / (self.grid.grid_size // 2))
                    c = tuple(int(col * intensity) for col in color)
                    self.grid.set_pixel(x, y, c)
        else:
            color = (255, 0, 255) if flash else (150, 0, 150)
            # Fill right side with color pulse
            for x in range(self.grid.grid_size // 2, self.grid.grid_size):
                for y in range(self.grid.grid_size):
                    intensity = (x - self.grid.grid_size // 2) / (self.grid.grid_size // 2)
                    c = tuple(int(col * intensity) for col in color)
                    self.grid.set_pixel(x, y, c)
        
        # Show current score
        self.grid.render_number(self.left_score, 3, 8, (255, 255, 255), scale=2)
        self.grid.render_number(self.right_score, 11, 8, (255, 255, 255), scale=2)
    
    def _render_game_over(self):
        """Render game over screen"""
        # Animated rainbow background
        time = pygame.time.get_ticks() / 1000.0
        for y in range(self.grid.grid_size):
            for x in range(self.grid.grid_size):
                hue = (x * 10 + y * 10 + time * 100) % 360
                color = hsv_to_rgb(hue, 0.5, 0.3)
                self.grid.set_pixel(x, y, color)
        
        # Winner text
        if self.winner == 'left':
            self.grid.render_text("P1", 5, 6, (0, 255, 255), scale=2)
        else:
            self.grid.render_text("P2", 5, 6, (255, 0, 255), scale=2)
        
        self.grid.render_text("WINS", 2, 12, (255, 255, 0), scale=1)
    
    def handle_input(self, keys, events):
        """Handle player input"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                # Mode selection
                if not self.mode_selected:
                    if event.key == pygame.K_LEFT:
                        self.mode_index = 0
                    elif event.key == pygame.K_RIGHT:
                        self.mode_index = 1
                    elif event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                        self.mode_selected = True
                        self.two_player_mode = (self.mode_index == 1)
                        self.reset_ball()
                
                # Start game
                elif not self.game_started and not self.game_over and self.score_animation_timer <= 0:
                    if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                        self.game_started = True
                
                # Return to menu
                if event.key == pygame.K_ESCAPE:
                    self.running = False
        
        # Paddle movement (continuous, smoother)
        if self.mode_selected and not self.game_over:
            move_speed = 0.8  # Smooth movement speed
            
            # Player 1 (left paddle)
            if keys[pygame.K_w]:
                self.left_paddle_y = max(0, self.left_paddle_y - move_speed)
            if keys[pygame.K_s]:
                self.left_paddle_y = min(self.grid.grid_size - self.paddle_height, 
                                        self.left_paddle_y + move_speed)
            
            # Player 2 (right paddle) - only in 2P mode
            if self.two_player_mode:
                if keys[pygame.K_UP]:
                    self.right_paddle_y = max(0, self.right_paddle_y - move_speed)
                if keys[pygame.K_DOWN]:
                    self.right_paddle_y = min(self.grid.grid_size - self.paddle_height, 
                                             self.right_paddle_y + move_speed)
