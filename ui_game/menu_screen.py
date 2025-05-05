import pygame
from constants import WIDTH, HEIGHT, WHITE, BLUE, GREEN, RED, YELLOW, PURPLE

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=WHITE, font_size=32):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font_size = font_size
        self.font = pygame.font.SysFont(None, font_size)
        self.is_hovered = False
        
    def draw(self, screen):
        # Draw button with hover effect
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=8)  # Border
        
        # Draw text
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered
        
    def is_clicked(self, mouse_pos, mouse_click):
        return self.rect.collidepoint(mouse_pos) and mouse_click


class MenuScreen:
    def __init__(self, game):
        self.game = game
        self.font_large = pygame.font.SysFont(None, 48)
        self.font = pygame.font.SysFont(None, 36)
        self.font_small = pygame.font.SysFont(None, 24)
        
        # Define buttons
        button_width = 220
        button_height = 60
        start_x = WIDTH // 2 - button_width // 2
        
        # Calculate positions for 5 level buttons
        level_width = 70
        level_spacing = 10
        total_levels_width = (level_width * 5) + (level_spacing * 4)
        level_start_x = (WIDTH - total_levels_width) // 2
        
        # Define colors for levels (green to red gradient)
        level_colors = [
            (50, 200, 50),    # Light Green
            (150, 200, 50),   # Yellow-Green
            (200, 200, 50),   # Yellow
            (200, 150, 50),   # Orange
            (200, 50, 50)     # Red
        ]
        
        level_hover_colors = [
            (100, 255, 100),  # Light Green Hover
            (180, 255, 100),  # Yellow-Green Hover
            (255, 255, 100),  # Yellow Hover
            (255, 180, 100),  # Orange Hover
            (255, 100, 100)   # Red Hover
        ]
        
        # Speed level buttons
        self.speed_buttons = []
        for i in range(5):
            x = level_start_x + (i * (level_width + level_spacing))
            self.speed_buttons.append(
                Button(x, 200, level_width, 50, str(i+1), level_colors[i], level_hover_colors[i], font_size=28)
            )
        
        # Objects level buttons
        self.objects_buttons = []
        for i in range(5):
            x = level_start_x + (i * (level_width + level_spacing))
            self.objects_buttons.append(
                Button(x, 320, level_width, 50, str(i+1), level_colors[i], level_hover_colors[i], font_size=28)
            )
        
        # Start game button
        self.start_button = Button(start_x, 450, button_width, button_height, 
                                   "START GAME", BLUE, (100, 150, 255))
    
    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check speed buttons
                for i, button in enumerate(self.speed_buttons):
                    if button.is_clicked(mouse_pos, True):
                        self.game.speed_level = i + 1
                
                # Check objects buttons
                for i, button in enumerate(self.objects_buttons):
                    if button.is_clicked(mouse_pos, True):
                        self.game.objects_level = i + 1
                
                # Check start button
                if self.start_button.is_clicked(mouse_pos, True):
                    self.game.start_game()
        
        # Update hover states
        for button in [*self.speed_buttons, *self.objects_buttons, self.start_button]:
            button.check_hover(mouse_pos)
    
    def update(self):
        # Nothing to update in the menu screen
        pass
    
    def draw(self, screen):
        # Fill background
        screen.fill((50, 50, 70))
        
        # Draw title
        title = self.font_large.render("OBSTACLE COURSE", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH // 2, 80))
        screen.blit(title, title_rect)
        
        # Draw section headers
        speed_text = self.font.render("Game Speed:", True, WHITE)
        screen.blit(speed_text, (WIDTH // 2 - speed_text.get_width() // 2, 150))
        
        # Draw level labels
        level_text_slow = self.font_small.render("Slow", True, WHITE)
        level_text_fast = self.font_small.render("Fast", True, WHITE)
        screen.blit(level_text_slow, (self.speed_buttons[0].rect.left, 175))
        screen.blit(level_text_fast, (self.speed_buttons[4].rect.right - level_text_fast.get_width(), 175))
        
        objects_text = self.font.render("Objects Amount:", True, WHITE)
        screen.blit(objects_text, (WIDTH // 2 - objects_text.get_width() // 2, 270))
        
        # Draw level labels for objects
        level_text_few = self.font_small.render("Few", True, WHITE)
        level_text_many = self.font_small.render("Many", True, WHITE)
        screen.blit(level_text_few, (self.objects_buttons[0].rect.left, 295))
        screen.blit(level_text_many, (self.objects_buttons[4].rect.right - level_text_many.get_width(), 295))
        
        # Draw buttons
        for button in self.speed_buttons:
            button.draw(screen)
            
        for button in self.objects_buttons:
            button.draw(screen)
            
        self.start_button.draw(screen)
        
        # Highlight selected options
        pygame.draw.rect(screen, WHITE, 
                         self.speed_buttons[self.game.speed_level - 1].rect, 4, border_radius=8)
        pygame.draw.rect(screen, WHITE, 
                         self.objects_buttons[self.game.objects_level - 1].rect, 4, border_radius=8)
        
        # Draw footer with instruction
        instruction = self.font_small.render("Select speed and objects amount, then click START", True, WHITE)
        instruction_rect = instruction.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        screen.blit(instruction, instruction_rect) 