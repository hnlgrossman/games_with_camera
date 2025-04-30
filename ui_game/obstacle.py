import pygame
import math
from constants import LANES, HEIGHT, RED, YELLOW, PURPLE

class Obstacle:
    def __init__(self, lane, size=60, color=RED, speed=8, shape="rect", obstacle_type="normal"):
        self.lane = lane
        self.size = size
        self.color = color
        self.speed = speed
        self.shape = shape
        self.obstacle_type = obstacle_type  # "normal", "jump", or "duck"
        self.x = LANES[lane] - size // 2
        self.y = -size
        self.rotation = 0  # For rotating obstacles
        
        # For jump and duck obstacles, we'll adjust the height
        if obstacle_type == "jump":
            # Wider and shorter obstacle to jump over
            self.height = size // 2
            self.width = size * 1.5
            self.rect = pygame.Rect(self.x - size // 4, self.y, self.width, self.height)
        elif obstacle_type == "duck":
            # Taller and narrower obstacle to duck under
            self.height = size * 1.5
            self.width = size
            self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        else:
            # Normal obstacle
            self.height = size
            self.width = size
            self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # For precise collision detection
        self.hitbox_reduction = 4 if shape == "circle" else 2
        self.collision_rect = pygame.Rect(
            self.x + self.hitbox_reduction, 
            self.y + self.hitbox_reduction, 
            self.width - (self.hitbox_reduction * 2), 
            self.height - (self.hitbox_reduction * 2)
        )
        
        # Visual indicator for jump/duck obstacles
        if obstacle_type == "jump":
            self.color = YELLOW
        elif obstacle_type == "duck": 
            self.color = PURPLE
    
    def move(self, delta_time=1.0):
        # Delta time allows for framerate-independent movement
        self.y += self.speed * delta_time
        self.rect.y = self.y
        self.collision_rect.y = self.y + self.hitbox_reduction
        
        # Add rotation for some obstacle types
        if self.shape in ["triangle", "rect"] and self.obstacle_type == "normal":
            self.rotation += 1.0 * delta_time
            if self.rotation >= 360:
                self.rotation = 0
    
    def draw(self, screen):
        if self.obstacle_type == "jump":
            # Draw a flat obstacle to jump over
            pygame.draw.rect(screen, self.color, self.rect)
            # Add an arrow pointing up
            pygame.draw.polygon(screen, (255, 255, 255),
                               [(self.x + self.width//2, self.y - 15),
                                (self.x + self.width//2 + 10, self.y + 5),
                                (self.x + self.width//2 - 10, self.y + 5)])
        
        elif self.obstacle_type == "duck":
            # Draw a tall obstacle to duck under
            pygame.draw.rect(screen, self.color, self.rect)
            # Add an arrow pointing down
            pygame.draw.polygon(screen, (255, 255, 255),
                               [(self.x + self.width//2, self.y + self.height + 15),
                                (self.x + self.width//2 + 10, self.y + self.height - 5),
                                (self.x + self.width//2 - 10, self.y + self.height - 5)])
        
        elif self.shape == "rect":
            if self.rotation > 0:
                # Draw rotated rectangle
                surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                pygame.draw.rect(surface, self.color, (0, 0, self.width, self.height))
                rotated = pygame.transform.rotate(surface, self.rotation)
                new_rect = rotated.get_rect(center=self.rect.center)
                screen.blit(rotated, new_rect.topleft)
            else:
                pygame.draw.rect(screen, self.color, self.rect)
        elif self.shape == "circle":
            pygame.draw.circle(screen, self.color, 
                              (self.x + self.width // 2, self.y + self.height // 2), 
                              self.width // 2)
        elif self.shape == "triangle":
            if self.rotation > 0:
                # Calculate rotated triangle points
                center_x = self.x + self.width // 2
                center_y = self.y + self.height // 2
                angle_rad = math.radians(self.rotation)
                
                # Original triangle points relative to center
                original_points = [
                    (0, -self.height // 2),  # Top
                    (-self.width // 2, self.height // 2),  # Bottom left
                    (self.width // 2, self.height // 2)  # Bottom right
                ]
                
                # Rotate points
                rotated_points = []
                for point in original_points:
                    x, y = point
                    rotated_x = x * math.cos(angle_rad) - y * math.sin(angle_rad)
                    rotated_y = x * math.sin(angle_rad) + y * math.cos(angle_rad)
                    rotated_points.append((center_x + rotated_x, center_y + rotated_y))
                
                pygame.draw.polygon(screen, self.color, rotated_points)
            else:
                points = [
                    (self.x + self.width // 2, self.y),
                    (self.x, self.y + self.height),
                    (self.x + self.width, self.y + self.height)
                ]
                pygame.draw.polygon(screen, self.color, points)
        
        # Draw hitbox for debug purposes (can be commented out in release)
        pygame.draw.rect(screen, (255, 255, 255), self.collision_rect, 1)
    
    def is_off_screen(self):
        return self.y > HEIGHT
        
    def get_collision_rect(self):
        return self.collision_rect
        
    def check_collision_with_player(self, player_rect, player):
        # First check if we're in the same lane (basic collision)
        if not self.collision_rect.colliderect(player_rect):
            return False
            
        # If we're colliding, check if the player's state matches the obstacle type
        if self.obstacle_type == "jump":
            # Player should be jumping to avoid collision
            return not player.jumping
        elif self.obstacle_type == "duck":
            # Player should be ducking to avoid collision
            return not player.ducking
        else:
            # Normal obstacle - any collision is a hit
            return True 