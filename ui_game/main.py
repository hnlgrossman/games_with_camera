import pygame
from constants import WIDTH, HEIGHT
from course_factory import CourseFactory
from game_engine import GameEngine

def main():
    # Initialize pygame
    pygame.init()
    
    # Create screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Obstacle Course")
    
    # Create courses
    courses = CourseFactory.create_all_courses()
    
    # Create and run game engine
    game = GameEngine(screen, courses)
    game.run()

if __name__ == "__main__":
    main() 