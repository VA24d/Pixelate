"""
Basketball Game - 2v2 with AI blocking, passing, and shooting
"""
import pygame
import random
import math
from games.base_game import Game, hsv_to_rgb


class Basketball(Game):
    """2v2 Basketball game with advanced AI"""
    
    def __init__(self, grid):
        super().__init__(grid)
        
        # Court dimensions
        self.court_width = self.grid.grid_size
        self.court_height = self.grid.grid_size
        
        # Players (x, y, team, has_ball)
        # Team 1 (left side) - Red/Miami Heat colors
        self.team1 = [
            {"x": 3.0, "y": 6.0, "team": 1, "color": (200, 30, 45)},
            {"x": 3.0, "y": 12.0, "team": 1, "color": (150, 20, 35)}
        ]
        
        # Team 2 (right side) - White/opposing team
        self.team2 = [
            {"x": 15.0, "y": 6.0, "team": 2, "color": (200, 200, 200)},
            {"x": 15.0, "y": 12.0, "team": 2, "color": (180, 180, 180)}
        ]
        
        # Ball
        self.ball_x = self.grid.grid_size / 2
        self.ball_y = self.grid.grid_size / 2
        self.ball_vx = 0
        self.ball_vy = 0
        # Not currently used as a continuous velocity, but kept for tuning.
        self.ball_speed = 8.0
        self.ball_holder = None  # Player index holding ball (0-3)
        self.ball_in_air = False
        self.ball_arc_progress = 0
        self.ball_arc_start = (0, 0)
        self.ball_arc_end = (0, 0)
        # Slightly slower arcs feels more realistic on a 19x19 grid.
        self.ball_arc_duration = 0.7
        
        # Hoops
        self.left_hoop_x = 1
        self.left_hoop_y = self.grid.grid_size // 2
        self.right_hoop_x = self.grid.grid_size - 2
        self.right_hoop_y = self.grid.grid_size // 2
        
        # Score
        self.team1_score = 0
        self.team2_score = 0
        self.max_score = 11
        self.score_animation_timer = 0
        self.scoring_team = None
        
        # Game state
        self.game_started = False
        self.game_over = False
        self.winner = None
        
        # Player control
        self.controlled_player = 0  # Player 1 controls team1[0]
        
        # AI settings
        self.ai_update_timer = 0
        # More frequent but smaller AI steps => smoother, less "teleporty".
        self.ai_update_interval = 0.06
        
        # Start with team 1 having the ball
        self.ball_holder = 0
        
    def update(self, dt: float):
        """Update game state"""
        if self.score_animation_timer > 0:
            self.score_animation_timer -= dt
            if self.score_animation_timer <= 0:
                self.scoring_team = None
                if not self.game_over:
                    self.reset_positions()
            return
        
        if self.game_over:
            return
        
        if not self.game_started:
            return
        
        # Update ball in air (shooting/passing)
        if self.ball_in_air:
            self.ball_arc_progress += dt / self.ball_arc_duration
            if self.ball_arc_progress >= 1.0:
                self.ball_in_air = False
                self.ball_x = self.ball_arc_end[0]
                self.ball_y = self.ball_arc_end[1]
                self.check_shot()
            else:
                # Calculate arc position
                t = self.ball_arc_progress
                self.ball_x = self.ball_arc_start[0] + (self.ball_arc_end[0] - self.ball_arc_start[0]) * t
                self.ball_y = self.ball_arc_start[1] + (self.ball_arc_end[1] - self.ball_arc_start[1]) * t
        
        # Update AI
        self.ai_update_timer += dt
        if self.ai_update_timer >= self.ai_update_interval:
            self.ai_update_timer = 0
            self.update_ai()
        
        # Update ball position if held
        if self.ball_holder is not None and not self.ball_in_air:
            player = self.get_player(self.ball_holder)
            self.ball_x = player["x"]
            self.ball_y = player["y"]
    
    def reset_positions(self):
        """Reset player and ball positions"""
        self.team1[0]["x"] = 3.0
        self.team1[0]["y"] = 6.0
        self.team1[1]["x"] = 3.0
        self.team1[1]["y"] = 12.0
        
        self.team2[0]["x"] = 15.0
        self.team2[0]["y"] = 6.0
        self.team2[1]["x"] = 15.0
        self.team2[1]["y"] = 12.0
        
        self.ball_x = self.grid.grid_size / 2
        self.ball_y = self.grid.grid_size / 2
        
        # Alternate possession
        if self.scoring_team == 1:
            self.ball_holder = 2  # Team 2 gets ball
        else:
            self.ball_holder = 0  # Team 1 gets ball
        
        self.ball_in_air = False
    
    def get_player(self, index):
        """Get player by index (0-3)"""
        if index < 2:
            return self.team1[index]
        else:
            return self.team2[index - 2]
    
    def get_all_players(self):
        """Get all players with their indices"""
        return [(0, self.team1[0]), (1, self.team1[1]), (2, self.team2[0]), (3, self.team2[1])]
    
    def update_ai(self):
        """Update AI for non-controlled players"""
        for idx, player in self.get_all_players():
            if idx == self.controlled_player:
                continue
            
            # AI behavior depends on ball possession
            if self.ball_holder == idx:
                # AI has the ball - decide to shoot or pass
                self.ai_with_ball(idx, player)
            elif self.ball_holder is None:
                # No one has ball - chase it
                self.ai_chase_ball(idx, player)
            elif self.get_player(self.ball_holder)["team"] == player["team"]:
                # Teammate has ball - position for pass
                self.ai_position_offense(idx, player)
            else:
                # Opponent has ball - defend/block
                self.ai_defend(idx, player)
    
    def ai_with_ball(self, idx, player):
        """AI behavior when holding the ball"""
        # Determine target hoop
        target_hoop_x = self.right_hoop_x if player["team"] == 1 else self.left_hoop_x
        target_hoop_y = self.right_hoop_y if player["team"] == 1 else self.left_hoop_y
        
        dist_to_hoop = math.sqrt((player["x"] - target_hoop_x)**2 + (player["y"] - target_hoop_y)**2)
        
        # Check if opponent is close (blocking)
        opponent_close = False
        for oidx, opponent in self.get_all_players():
            if opponent["team"] != player["team"]:
                dist = math.sqrt((player["x"] - opponent["x"])**2 + (player["y"] - opponent["y"])**2)
                if dist < 3:
                    opponent_close = True
                    break
        
        # Decision making
        if dist_to_hoop < 6 and not opponent_close:
            # Close enough to shoot
            self.shoot(idx, target_hoop_x, target_hoop_y)
        elif opponent_close:
            # Pass to teammate
            self.ai_pass(idx, player)
        else:
            # Move towards hoop
            self.ai_move_towards(player, target_hoop_x, target_hoop_y)
    
    def ai_pass(self, idx, player):
        """AI passes to teammate"""
        # Find teammate
        for tidx, teammate in self.get_all_players():
            if teammate["team"] == player["team"] and tidx != idx:
                self.pass_ball(idx, tidx)
                break
    
    def ai_chase_ball(self, idx, player):
        """AI chases loose ball"""
        self.ai_move_towards(player, self.ball_x, self.ball_y)
        
        # Pick up ball if close
        dist = math.sqrt((player["x"] - self.ball_x)**2 + (player["y"] - self.ball_y)**2)
        if dist < 1.5:
            self.ball_holder = idx
    
    def ai_position_offense(self, idx, player):
        """AI positions for receiving pass"""
        # Move towards opponent's hoop but stay spread out
        target_x = 12 if player["team"] == 1 else 6
        target_y = 9 if idx % 2 == 0 else 14
        self.ai_move_towards(player, target_x, target_y, speed=0.45)
    
    def ai_defend(self, idx, player):
        """AI defends against ball carrier"""
        if self.ball_holder is not None:
            ball_carrier = self.get_player(self.ball_holder)
            # Move towards ball carrier to block
            self.ai_move_towards(player, ball_carrier["x"], ball_carrier["y"], speed=0.5)
            
            # Attempt steal if very close
            dist = math.sqrt((player["x"] - ball_carrier["x"])**2 + (player["y"] - ball_carrier["y"])**2)
            if dist < 1.5 and random.random() < 0.08:
                # Steal!
                self.ball_holder = idx
    
    def ai_move_towards(self, player, target_x, target_y, speed=0.55):
        """Move player towards target"""
        dx = target_x - player["x"]
        dy = target_y - player["y"]
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist > 0.5:
            player["x"] += (dx / dist) * speed
            player["y"] += (dy / dist) * speed
            
            # Keep in bounds
            player["x"] = max(1, min(self.court_width - 2, player["x"]))
            player["y"] = max(1, min(self.court_height - 2, player["y"]))
    
    def shoot(self, player_idx, target_x, target_y):
        """Player shoots at hoop"""
        player = self.get_player(player_idx)
        self.ball_arc_start = (player["x"], player["y"])
        self.ball_arc_end = (target_x, target_y)
        self.ball_arc_progress = 0
        self.ball_in_air = True
        self.ball_holder = None
        self.shooter = player_idx
    
    def pass_ball(self, from_idx, to_idx):
        """Pass ball between players"""
        from_player = self.get_player(from_idx)
        to_player = self.get_player(to_idx)
        
        self.ball_arc_start = (from_player["x"], from_player["y"])
        self.ball_arc_end = (to_player["x"], to_player["y"])
        self.ball_arc_progress = 0
        self.ball_arc_duration = 0.45  # Slightly slower for readability
        self.ball_in_air = True
        self.ball_holder = None
        self.pass_target = to_idx
    
    def check_shot(self):
        """Check if shot scores"""
        # Check if pass - give ball to target
        if hasattr(self, 'pass_target'):
            self.ball_holder = self.pass_target
            delattr(self, 'pass_target')
            self.ball_arc_duration = 0.5
            return
        
        # Check if shot scores
        shooter = self.get_player(self.shooter)
        target_hoop_x = self.right_hoop_x if shooter["team"] == 1 else self.left_hoop_x
        target_hoop_y = self.right_hoop_y if shooter["team"] == 1 else self.left_hoop_y
        
        dist = math.sqrt((self.ball_x - target_hoop_x)**2 + (self.ball_y - target_hoop_y)**2)
        
        # Score if close enough (with some randomness)
        if dist < 2.5 and random.random() < 0.7:
            if shooter["team"] == 1:
                self.team1_score += 2
                self.scoring_team = 1
            else:
                self.team2_score += 2
                self.scoring_team = 2
            
            self.score_animation_timer = 1.0
            
            # Check for win
            if self.team1_score >= self.max_score:
                self.game_over = True
                self.winner = 1
            elif self.team2_score >= self.max_score:
                self.game_over = True
                self.winner = 2
        else:
            # Missed shot - ball is loose
            self.ball_holder = None
    
    def render(self):
        """Render the basketball game"""
        self.grid.clear((20, 50, 20))  # Green court
        
        if self.score_animation_timer > 0:
            self._render_score_animation()
            return
        
        if self.game_over:
            self._render_game_over()
            return
        
        # Draw court lines
        # Center line
        for y in range(self.court_height):
            self.grid.set_pixel(self.court_width // 2, y, (255, 255, 255))
        
        # Hoops
        self.grid.set_pixel(self.left_hoop_x, self.left_hoop_y, (255, 100, 0))
        self.grid.set_pixel(self.left_hoop_x, self.left_hoop_y - 1, (255, 100, 0))
        self.grid.set_pixel(self.left_hoop_x, self.left_hoop_y + 1, (255, 100, 0))
        
        self.grid.set_pixel(self.right_hoop_x, self.right_hoop_y, (255, 100, 0))
        self.grid.set_pixel(self.right_hoop_x, self.right_hoop_y - 1, (255, 100, 0))
        self.grid.set_pixel(self.right_hoop_x, self.right_hoop_y + 1, (255, 100, 0))
        
        # Draw players
        for idx, player in self.get_all_players():
            color = player["color"]
            px, py = int(player["x"]), int(player["y"])
            
            # Highlight controlled player
            if idx == self.controlled_player:
                # Brighter color
                color = tuple(min(255, c + 50) for c in color)
            
            self.grid.set_pixel(px, py, color)
        
        # Draw ball
        if not self.ball_in_air or True:  # Always show ball
            bx, by = int(self.ball_x), int(self.ball_y)
            ball_color = (255, 140, 0) if not self.ball_in_air else (255, 200, 100)
            if 0 <= bx < self.court_width and 0 <= by < self.court_height:
                self.grid.set_pixel(bx, by, ball_color)
        
        # Draw scores
        self.grid.render_number(self.team1_score, 2, 1, (255, 255, 255), scale=1)
        self.grid.render_number(self.team2_score, 14, 1, (255, 255, 255), scale=1)
    
    def _render_score_animation(self):
        """Render scoring animation"""
        flash = int(self.score_animation_timer * 8) % 2
        
        if self.scoring_team == 1:
            color = (200, 30, 45) if flash else (100, 15, 22)
        else:
            color = (200, 200, 200) if flash else (100, 100, 100)
        
        self.grid.clear(color)
        
        # Show scores larger
        self.grid.render_number(self.team1_score, 3, 8, (255, 255, 255), scale=2)
        self.grid.render_number(self.team2_score, 11, 8, (255, 255, 255), scale=2)
    
    def _render_game_over(self):
        """Render game over screen"""
        # Winner color background
        if self.winner == 1:
            bg_color = (200, 30, 45)
            text = "RED"
        else:
            bg_color = (200, 200, 200)
            text = "WHT"
        
        self.grid.clear(bg_color)
        
        self.grid.render_text(text, 4, 6, (255, 255, 0), scale=2)
        self.grid.render_text("WINS", 2, 12, (255, 255, 255), scale=1)
    
    def handle_input(self, keys, events):
        """Handle player input"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                # Start game
                if not self.game_started:
                    if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                        self.game_started = True
                
                # Shoot
                if event.key == pygame.K_SPACE and self.ball_holder == self.controlled_player:
                    player = self.get_player(self.controlled_player)
                    target_x = self.right_hoop_x if player["team"] == 1 else self.left_hoop_x
                    target_y = self.right_hoop_y if player["team"] == 1 else self.left_hoop_y
                    self.shoot(self.controlled_player, target_x, target_y)
                
                # Pass
                if event.key == pygame.K_p and self.ball_holder == self.controlled_player:
                    # Pass to teammate
                    for tidx, teammate in self.get_all_players():
                        if teammate["team"] == self.get_player(self.controlled_player)["team"] and tidx != self.controlled_player:
                            self.pass_ball(self.controlled_player, tidx)
                            break
                
                # Return to menu
                if event.key == pygame.K_ESCAPE:
                    self.running = False
        
        # Player movement (continuous)
        if self.game_started and not self.game_over:
            player = self.get_player(self.controlled_player)
            move_speed = 0.6
            
            if keys[pygame.K_w]:
                player["y"] = max(1, player["y"] - move_speed)
            if keys[pygame.K_s]:
                player["y"] = min(self.court_height - 2, player["y"] + move_speed)
            if keys[pygame.K_a]:
                player["x"] = max(1, player["x"] - move_speed)
            if keys[pygame.K_d]:
                player["x"] = min(self.court_width - 2, player["x"] + move_speed)
