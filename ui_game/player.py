import pygame
from constants import LANES, HEIGHT, BLUE

class Player:
    def __init__(self, size=60, color=BLUE, speed=1):
        self.size = size
        self.color = color
        self.lane = 1  # Start in middle lane
        self.speed = speed
        self.target_lane = 1  # For smooth movement
        self.moving = False
        self.x = LANES[self.lane] - self.size // 2
        self.y = HEIGHT - self.size - 20
        self.move_speed = 12  # Pixels per frame during lane change
        
        # For jumping and ducking
        self.default_y = HEIGHT - self.size - 40
        self.jumping = False
        self.ducking = False
        self.duck_height = self.size // 2
        self.default_size = size
        
        # Timing for jump and duck actions
        self.action_start_time = 0
        self.action_duration = 1500  # 1.5 seconds in milliseconds
        
        # For size changes during jump
        self.jump_size_multiplier = 1.3  # Make player 30% bigger when jumping
        self.duck_size_multiplier = 0.6  # Make player 30% bigger when jumping
        self.current_size = size
    
    def update(self):
        current_time = pygame.time.get_ticks()
        
        if self.moving:
            target_x = LANES[self.target_lane] - self.size // 2
            if abs(self.x - target_x) <= self.move_speed:
                # Reached target position
                self.x = target_x
                self.lane = self.target_lane
                self.moving = False
            else:
                # Move towards target
                direction = 1 if target_x > self.x else -1
                self.x += direction * self.move_speed
        
        # Update jumping (just size change)
        if self.jumping:
            # Check if jump duration has elapsed
            if current_time - self.action_start_time >= self.action_duration:
                self.jumping = False
                self.current_size = self.default_size
            else:
                # Keep player bigger during jump duration
                self.current_size = int(self.default_size * self.jump_size_multiplier)
        
        # Update ducking
        if self.ducking:
            # Check if duck duration has elapsed
            if current_time - self.action_start_time >= self.action_duration:
                self.ducking = False
                self.current_size = self.default_size
                self.y = self.default_y
            else:
                # Keep player bigger during jump duration
                self.current_size = int(self.default_size * self.duck_size_multiplier)
            # No need to update position during duck as it's set in the duck() method
    
    def draw(self, screen):
        # Calculate center position to maintain player position when size changes
        center_x = self.x + self.size // 2
        center_y = self.y + self.size // 2
        
        # Draw player with current size
        pygame.draw.rect(screen, self.color, 
                        (center_x - self.current_size // 2,
                         center_y - self.current_size // 2,
                         self.current_size,
                         self.current_size))
        
        # Draw hitbox outline for precision
        pygame.draw.rect(screen, (255, 255, 255), 
                        (center_x - self.current_size // 2,
                         center_y - self.current_size // 2,
                         self.current_size,
                         self.current_size), 1)
    
    def get_rect(self):
        # Return rectangle with current size
        center_x = self.x + self.size // 2
        center_y = self.y + self.size // 2
        return pygame.Rect(center_x - self.current_size // 2,
                         center_y - self.current_size // 2,
                         self.current_size,
                         self.current_size)
        
    def move_left(self):
        if not self.moving and self.lane > 0:
            self.target_lane = self.lane - 1
            self.moving = True
            return True
        return False
            
    def move_right(self):
        if not self.moving and self.lane < 2:
            self.target_lane = self.lane + 1
            self.moving = True
            return True
        return False
    
    def jump(self):
        if not self.jumping and not self.ducking:
            self.jumping = True
            self.action_start_time = pygame.time.get_ticks()
            return True
        return False
        
    def duck(self):
        if not self.jumping and not self.ducking:
            self.ducking = True
            self.current_size = self.duck_height
            self.y = self.default_y + (self.default_size - self.duck_height)
            self.action_start_time = pygame.time.get_ticks()
            return True
        return False
        
    def release_duck(self):
        if self.ducking:
            current_time = pygame.time.get_ticks()
            # Only allow release if the duration has elapsed
            if current_time - self.action_start_time >= self.action_duration:
                self.ducking = False
                self.y = self.default_y
                self.current_size = self.default_size
                return True
        return False 