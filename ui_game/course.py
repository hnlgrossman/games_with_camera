import random
import pygame
from player import Player
from obstacle import Obstacle
from constants import WHITE

class Course:
    def __init__(self, name, background_color, player_config, obstacle_configs):
        self.name = name
        self.background_color = background_color
        self.player = Player(**player_config)
        self.obstacle_configs = obstacle_configs
        self.obstacles = []
        self.spawn_timer = 0
        self.spawn_rate = obstacle_configs.get("spawn_rate", 60)
        self.score = 0
        self.distance = 0  # Track distance traveled
        self.start_time = pygame.time.get_ticks()
        self.last_frame_time = pygame.time.get_ticks()
        self.best_score = 0
        self.best_time = 0
        self.paused = False
        
        # Gradually increase difficulty
        self.difficulty_multiplier = 1.0
        self.difficulty_increase_rate = obstacle_configs.get("difficulty_increase_rate", 0.005)
        self.max_difficulty = obstacle_configs.get("max_difficulty", 2.0)
    
    def spawn_obstacle(self):
        # Intelligent obstacle spawning - avoid creating impossible patterns
        safe_lanes = [0, 1, 2]
        
        # Check recent obstacles to avoid creating impossible-to-dodge patterns
        recent_obstacles = [ob for ob in self.obstacles if ob.y < 0]
        if recent_obstacles:
            for ob in recent_obstacles:
                if ob.y > -ob.size * 2:  # If obstacle is close to entering screen
                    if ob.lane in safe_lanes and len(safe_lanes) > 1:
                        safe_lanes.remove(ob.lane)
        
        # Choose from safe lanes or any lane if no safe ones
        lane = random.choice(safe_lanes) if safe_lanes else random.randint(0, 2)
        
        # Apply difficulty multiplier to obstacle speed
        obstacle_type = random.choice(self.obstacle_configs["types"])
        adjusted_obstacle = obstacle_type.copy()  # Create a copy to avoid modifying original
        adjusted_obstacle["speed"] *= self.difficulty_multiplier
        
        self.obstacles.append(Obstacle(lane, **adjusted_obstacle))
    
    def update(self):
        if self.paused:
            return
            
        # Calculate delta time for frame-rate independent movement
        current_time = pygame.time.get_ticks()
        delta_time = (current_time - self.last_frame_time) / 16.667  # Normalized to 60fps
        self.last_frame_time = current_time
        
        # Update the player
        self.player.update()
        
        # Gradually increase difficulty
        self.difficulty_multiplier = min(
            self.difficulty_multiplier + self.difficulty_increase_rate * delta_time,
            self.max_difficulty
        )
        
        # Track distance (for score)
        self.distance += 0.1 * delta_time * self.difficulty_multiplier
        
        # Spawn obstacles
        self.spawn_timer += delta_time
        spawn_threshold = self.spawn_rate / self.difficulty_multiplier
        if self.spawn_timer > spawn_threshold:
            self.spawn_obstacle()
            self.spawn_timer = 0
        
        # Move obstacles
        for obstacle in self.obstacles:
            obstacle.move(delta_time)
        
        # Remove off-screen obstacles and increase score
        new_obstacles = []
        for ob in self.obstacles:
            if ob.is_off_screen():
                self.score += 1
            else:
                new_obstacles.append(ob)
        self.obstacles = new_obstacles
    
    def draw(self, screen):
        screen.fill(self.background_color)
        
        # Draw lane markers
        for lane in range(3):
            lane_x = lane * (screen.get_width() // 3) + (screen.get_width() // 6)
            pygame.draw.line(screen, (100, 100, 100), 
                             (lane_x, 0), (lane_x, screen.get_height()), 1)
        
        # Draw obstacles and player
        for obstacle in self.obstacles:
            obstacle.draw(screen)
        self.player.draw(screen)
        
        # Display UI elements with a semi-transparent background
        self._draw_ui(screen)
    
    def _draw_ui(self, screen):
        # Create a semi-transparent overlay for UI
        ui_overlay = pygame.Surface((screen.get_width(), 120), pygame.SRCALPHA)
        ui_overlay.fill((0, 0, 0, 128))
        screen.blit(ui_overlay, (0, 0))
        
        # Display course name
        font = pygame.font.SysFont(None, 36)
        text = font.render(self.name, True, WHITE)
        screen.blit(text, (10, 10))
        
        # Display score
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 50))
        
        # Display elapsed time
        elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
        time_text = font.render(f"Time: {elapsed_time}s", True, WHITE)
        screen.blit(time_text, (10, 90))
        
        # Display difficulty
        difficulty_text = font.render(
            f"Difficulty: {self.difficulty_multiplier:.1f}x", True, WHITE
        )
        screen.blit(difficulty_text, (screen.get_width() - 200, 10))
        
        # Display best score
        if self.best_score > 0:
            best_score_text = font.render(f"Best: {self.best_score}", True, WHITE)
            screen.blit(best_score_text, (screen.get_width() - 200, 50))
    
    def check_collision(self):
        player_rect = self.player.get_rect()
        for obstacle in self.obstacles:
            if obstacle.check_collision_with_player(player_rect, self.player):
                # Update best score
                if self.score > self.best_score:
                    self.best_score = self.score
                
                # Update best time
                elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
                if elapsed_time > self.best_time:
                    self.best_time = elapsed_time
                    
                return True
        return False
    
    def toggle_pause(self):
        self.paused = not self.paused
        
    def reset(self):
        self.obstacles = []
        self.spawn_timer = 0
        self.score = 0
        self.distance = 0
        self.difficulty_multiplier = 1.0
        self.start_time = pygame.time.get_ticks()
        self.last_frame_time = pygame.time.get_ticks()
        self.paused = False 