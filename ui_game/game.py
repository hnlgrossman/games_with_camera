from enum import Enum

class GameState(Enum):
    MENU = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3

class Game:
    def __init__(self):
        self.state = GameState.MENU
        self.speed_level = 1  # 1 to 5
        self.objects_level = 1  # 1 to 5
        
    def get_speed_multiplier(self):
        # Adjusted for 5 levels: 0.8, 1.0, 1.2, 1.4, 1.6
        return 0.6 + (self.speed_level * 0.2)
        
    def get_objects_multiplier(self):
        # Adjusted for 5 levels: 0.8, 1.0, 1.2, 1.4, 1.6
        return 0.6 + (self.objects_level * 0.2)
        
    def start_game(self):
        self.state = GameState.PLAYING
        
    def pause_game(self):
        if self.state == GameState.PLAYING:
            self.state = GameState.PAUSED
        elif self.state == GameState.PAUSED:
            self.state = GameState.PLAYING
            
    def go_to_menu(self):
        self.state = GameState.MENU
        
    def game_over(self):
        self.state = GameState.GAME_OVER 