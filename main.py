#!/usr/bin/env python3
"""
LED Grid Game Console Simulator
19x19 RGB LED Grid with Game Selection Menu

Controls:
  Boot/Menu:
    - LEFT/RIGHT: Navigate games
    - SPACE/ENTER: Select game
    - M: Toggle smooth/instant carousel transitions
  
  Pong:
    - W/S: Player 1 paddle (left)
    - UP/DOWN: Player 2 paddle (right, 2P mode only)
    - ESC: Return to menu
  
  LED Grid Adjustments (anytime):
    - +/-: Adjust LED size
    - [/]: Adjust LED spacing
    - ,/.: Adjust LED gap
    - T: Toggle circular/square LED style
    - L: Toggle portrait/landscape window layout
    - Q: Quit application
"""
import pygame
import sys
from led_grid import LEDGrid
from games.base_game import GameState, GameManager
from games.boot_screen import BootScreen
from games.menu import CarouselMenu
from games.pong import Pong
from games.basketball import Basketball
from games.snake import Snake
from games.flappy import Flappy
from games.pet_game import PetGame
from games import sound
from games.vacation import VacationGallery
from games.shadow_fight import ShadowFight
from games.asphalt_race import AsphaltRace
from games.overlay_editor import OverlayEditor


class LEDGameConsole:
    """Main application - LED Grid Game Console"""
    
    def __init__(self):
        pygame.init()
        
        # Window setup
        self.portrait_size = (1000, 1000)
        self.landscape_size = (1400, 900)
        self.is_landscape = False

        self.window_width, self.window_height = self.portrait_size
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("LED Grid Game Console - 19x19")
        
        # LED Grid
        self.grid = LEDGrid(self.window_width, self.window_height)
        
        # Game Manager
        self.manager = GameManager(self.grid)
        
        # Clock for frame rate
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Current state
        self.current_screen = None
        self.show_boot = True

        # Bottom help overlay (pygame text). Hide by default during gameplay.
        self.show_help_overlay = True

        # Editor resume support
        self._resume_state = None
        self._resume_screen = None
        self._resume_menu_index = 0
        
        # Start with boot screen
        self.start_boot_screen()
    
    def start_boot_screen(self):
        """Start the boot animation"""
        self.current_screen = BootScreen(self.grid)
        self.manager.set_state(GameState.BOOT)
        self.show_help_overlay = True
    
    def start_menu(self, initial_index: int = 0):
        """Start the carousel menu"""
        self.current_screen = CarouselMenu(self.grid, self.manager)
        # restore selection if requested
        try:
            self.current_screen.selected_index = int(initial_index)
            self.current_screen.target_index = int(initial_index)
            if not self.current_screen.smooth_transition:
                self.current_screen.current_offset = float(initial_index)
        except Exception:
            pass
        self.manager.set_state(GameState.MENU)
        self.show_help_overlay = True
    
    def start_game(self, game_index: int):
        """Start a specific game by index"""
        if game_index == 0:
            self.current_screen = Pong(self.grid)
        elif game_index == 1:
            self.current_screen = Snake(self.grid)
        elif game_index == 2:
            self.current_screen = Flappy(self.grid)
        elif game_index == 3:
            self.current_screen = Basketball(self.grid)
        elif game_index == 4:
            self.current_screen = PetGame(self.grid)
        elif game_index == 5:
            self.current_screen = VacationGallery(self.grid)
        elif game_index == 6:
            self.current_screen = ShadowFight(self.grid)
        elif game_index == 7:
            self.current_screen = AsphaltRace(self.grid)
        
        self.manager.set_state(GameState.PLAYING)
        self.show_help_overlay = False

    def _start_editor(self, sprite_name: str, w: int, h: int):
        # Remember where to go back
        self._resume_state = self.manager.state
        self._resume_screen = self.current_screen
        if isinstance(self.current_screen, CarouselMenu):
            self._resume_menu_index = int(self.current_screen.selected_index)
        self.current_screen = OverlayEditor(self.grid, sprite_name=sprite_name, w=w, h=h)
        self.manager.set_state(GameState.EDITOR)
        # overlay is useful in editor
        self.show_help_overlay = True

    def _resume_from_editor(self):
        # Default to menu if something is missing.
        if self._resume_state == GameState.PLAYING and self._resume_screen is not None:
            self.current_screen = self._resume_screen
            self.manager.set_state(GameState.PLAYING)
            self.show_help_overlay = False
        else:
            self.start_menu(self._resume_menu_index)

        self._resume_state = None
        self._resume_screen = None
    
    def handle_global_input(self, keys, events):
        """Handle global input (LED grid adjustments and quit)"""
        for event in events:
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                # Quit
                if event.key == pygame.K_q:
                    return False

                # Toggle bottom help overlay
                if event.key == pygame.K_h:
                    self.show_help_overlay = not self.show_help_overlay

                # Edit mode: menu logos + a few HUD sprites
                if event.key == pygame.K_e:
                    if self.manager.state == GameState.MENU and isinstance(self.current_screen, CarouselMenu):
                        name = self.current_screen.games[self.current_screen.selected_index]["name"]
                        self._start_editor(sprite_name=f"menu_logo_{name}", w=11, h=8)
                    elif self.manager.state == GameState.PLAYING and isinstance(self.current_screen, AsphaltRace):
                        # Shift+E edits SCORE icon, E edits DIST icon
                        mods = pygame.key.get_mods()
                        if mods & pygame.KMOD_SHIFT:
                            self._start_editor(sprite_name="hud_race_score", w=3, h=5)
                        else:
                            self._start_editor(sprite_name="hud_race_dist", w=3, h=5)
                
                # LED adjustments
                if event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    self.grid.adjust_led_size(2)
                elif event.key == pygame.K_MINUS:
                    self.grid.adjust_led_size(-2)
                elif event.key == pygame.K_LEFTBRACKET:
                    self.grid.adjust_led_spacing(-1)
                elif event.key == pygame.K_RIGHTBRACKET:
                    self.grid.adjust_led_spacing(1)
                elif event.key == pygame.K_COMMA:
                    self.grid.adjust_led_gap(-1)
                elif event.key == pygame.K_PERIOD:
                    self.grid.adjust_led_gap(1)
                elif event.key == pygame.K_t:
                    self.grid.toggle_style()
                elif event.key == pygame.K_l:
                    # Toggle window orientation (portrait/landscape)
                    self.is_landscape = not self.is_landscape
                    (self.window_width, self.window_height) = (
                        self.landscape_size if self.is_landscape else self.portrait_size
                    )
                    self.screen = pygame.display.set_mode((self.window_width, self.window_height))
                    self.grid.update_window_size(self.window_width, self.window_height)
                elif event.key == pygame.K_o:
                    # Optional sound toggle
                    enabled = sound.toggle_enabled()
                    # feedback beep on toggle (only if enabling)
                    if enabled:
                        sound.play_beep(880, 60)
        
        return True
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            # Calculate delta time
            dt = self.clock.tick(self.fps) / 1000.0  # Convert to seconds
            
            # Get input
            keys = pygame.key.get_pressed()
            events = pygame.event.get()
            
            # Handle global input (LED adjustments, quit)
            running = self.handle_global_input(keys, events)
            if not running:
                break
            
            # Update current screen
            if self.current_screen:
                self.current_screen.update(dt)
                
                # Handle state transitions
                if not self.current_screen.is_running():
                    if self.manager.state == GameState.BOOT:
                        self.start_menu()
                    elif self.manager.state == GameState.MENU:
                        # Start selected game
                        self.start_game(self.manager.selected_game_index)
                    elif self.manager.state == GameState.EDITOR:
                        self._resume_from_editor()
                    elif self.manager.state == GameState.PLAYING:
                        # Return to menu
                        self.start_menu()
                else:
                    # Handle screen-specific input
                    self.current_screen.handle_input(keys, events)
            
            # Render current screen
            self.screen.fill((0, 0, 0))  # Black background
            if self.current_screen:
                self.current_screen.render()
            
            # Render LED grid
            self.grid.render(self.screen)
            
            # Display help text
            if self.show_help_overlay:
                self._render_help_text()
            
            # Update display
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()
    
    def _render_help_text(self):
        """Render help text at bottom of screen"""
        font = pygame.font.Font(None, 20)
        
        help_texts = [
            "Controls: +/- Size | [/] Spacing | ,/. Gap | T Style | L Layout | O Sound | H Help | Q Quit",
        ]
        
        if self.manager.state == GameState.MENU:
            help_texts.append("Menu: LEFT/RIGHT Navigate | SPACE/ENTER Select | M Toggle Transition | E Edit Logo")
        elif self.manager.state == GameState.PLAYING:
            # Contextual hints based on current game
            if isinstance(self.current_screen, Pong):
                help_texts.append("Pong: W/S | (2P: UP/DOWN) | SPACE Start | ESC Menu")
            elif isinstance(self.current_screen, Snake):
                help_texts.append("Snake: ARROWS Move | ESC Menu")
            elif isinstance(self.current_screen, Flappy):
                help_texts.append("Flappy: SPACE Flap | R Restart | ESC Menu")
            elif isinstance(self.current_screen, Basketball):
                help_texts.append("Bball: WASD Move | SPACE Shoot | P Pass | ESC Menu")
            elif isinstance(self.current_screen, PetGame):
                help_texts.append("Pets: LR Switch | A Feed | S Play | D Rest | ESC Menu")
            elif isinstance(self.current_screen, ShadowFight):
                help_texts.append("Fight: A/D Move | W Jump | J Punch | ESC Menu")
            elif isinstance(self.current_screen, AsphaltRace):
                help_texts.append("Race: LR Steer | UP Gas | DOWN Brake | E Edit HUD | ESC Menu")
            else:
                help_texts.append("Game: ESC Menu")
        
        y_offset = self.window_height - 60
        for text in help_texts:
            surface = font.render(text, True, (200, 200, 200))
            rect = surface.get_rect(center=(self.window_width // 2, y_offset))
            self.screen.blit(surface, rect)
            y_offset += 25


def main():
    """Entry point"""
    console = LEDGameConsole()
    console.run()


if __name__ == "__main__":
    main()