import pygame
import sys
from constants import WIDTH, HEIGHT, FPS
from course_factory import CourseFactory
from game_engine import GameEngine
from game import Game, GameState
from menu_screen import MenuScreen

def main():
    # Initialize pygame
    pygame.init()
    
    # Create screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Obstacle Course")
    
    # Create game state manager
    game = Game()
    
    # Create menu screen
    menu = MenuScreen(game)
    
    # Create courses
    courses = CourseFactory.create_all_courses()
    
    # Create game engine (but don't run it yet)
    game_engine = GameEngine(screen, courses)
    game_engine.run()
    
    # Main game loop
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # Handle events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game.state == GameState.PLAYING:
                        game.pause_game()
                    elif game.state == GameState.PAUSED:
                        game.pause_game()
                    else:
                        running = False
        
        # Game state machine
        if game.state == GameState.MENU:
            # Menu mode
            menu.handle_events(events)
            menu.update()
            menu.draw(screen)
        elif game.state in [GameState.PLAYING, GameState.PAUSED]:
            # Apply game settings to engine
            game_engine.current_course.speed_multiplier = game.get_speed_multiplier()
            game_engine.current_course.objects_multiplier = game.get_objects_multiplier()
            
            # Let the game engine handle the gameplay
            game_engine.handle_events()
            game_engine.handle_player_input()
            
            if not game_engine.paused:
                game_engine.paused = (game.state == GameState.PAUSED)
            elif game_engine.paused and game.state == GameState.PLAYING:
                game_engine.paused = False
                
            game_engine.update()
            game_engine.render()
            
            # Check if game engine wants to exit
            if not game_engine.running:
                running = False
                
        # Update display and maintain frame rate
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 