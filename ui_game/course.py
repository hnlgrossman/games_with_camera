import random
import pygame
from player import Player
from obstacle import Obstacle
from constants import WHITE, LANES

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
        
        # Settings from game menu
        self.speed_multiplier = 1.0
        self.objects_multiplier = 1.0
        
        # Gradually increase difficulty
        self.difficulty_multiplier = 1.0
        self.difficulty_increase_rate = obstacle_configs.get("difficulty_increase_rate", 0.005)
        self.max_difficulty = obstacle_configs.get("max_difficulty", 2.0)
        
        # Keep track of obstacle positions to ensure valid paths
        self.obstacle_y_positions = []
    
    def ensure_valid_path(self, lanes_with_obstacles, y_position, vertical_safety_distance=150):
        """Check if there's at least one free lane or if all three lanes have obstacles at the same height"""
        
        # If not all lanes have obstacles at this position, there's a valid path
        if len(lanes_with_obstacles) < 3:
            return True
            
        # Check existing obstacles to see if there's a valid path vertically
        for obstacle in self.obstacles:
            # Calculate distance between this y_position and existing obstacle y position
            distance = abs(obstacle.y - y_position)
            
            # If an obstacle is too close vertically in the same lane, it might be impossible to pass
            if distance < vertical_safety_distance and obstacle.lane in lanes_with_obstacles:
                return False
                
        return True
    
    def spawn_obstacle(self):
        # Intelligent obstacle spawning - avoid creating impossible patterns
        safe_lanes = [0, 1, 2]
        
        # Check recent obstacles to avoid creating impossible-to-dodge patterns
        recent_obstacles = [ob for ob in self.obstacles if ob.y < 0]
        lanes_with_obstacles_at_same_height = {}
        
        if recent_obstacles:
            for ob in recent_obstacles:
                # Group obstacles by their approximate y position (+/- 20 pixels)
                y_group = ob.y // 20 * 20
                if y_group not in lanes_with_obstacles_at_same_height:
                    lanes_with_obstacles_at_same_height[y_group] = []
                lanes_with_obstacles_at_same_height[y_group].append(ob.lane)
                
                # Remove lane from safe lanes if obstacle is close to entering screen
                if ob.y > -ob.size * 2 and ob.lane in safe_lanes and len(safe_lanes) > 1:
                    safe_lanes.remove(ob.lane)
        
        # Determine how many obstacles to spawn based on objects_level
        # Level 1: Single obstacle
        # Level 2-3: Occasionally spawn 2 obstacles
        # Level 4: Regularly spawn 2 obstacles, occasionally 3
        # Level 5: Regularly spawn 2-3 obstacles
        
        num_obstacles = 1
        objects_level_int = int(self.objects_multiplier * 5) - 2  # Convert to 0-3 range
        
        if objects_level_int >= 0:  # Level 2 or higher
            if random.random() < (0.25 * objects_level_int):
                num_obstacles += 1
                
        if objects_level_int >= 2:  # Level 4 or higher
            if random.random() < (0.2 * (objects_level_int - 1)):
                num_obstacles += 1
        
        # NEVER use all 3 lanes at once - this would create an impossible situation
        num_obstacles = min(num_obstacles, len(safe_lanes), 2)  # Maximum 2 obstacles, not 3
        
        # Calculate spacing between obstacles (higher levels = closer together)
        min_spacing = max(100, 150 - (objects_level_int * 15))
        
        # Apply difficulty and speed multipliers to obstacle speed
        obstacle_type = random.choice(self.obstacle_configs["types"])
        
        # Spawn the obstacles
        if num_obstacles > 0 and safe_lanes:
            lanes_to_use = random.sample(safe_lanes, num_obstacles)
            
            for i, lane in enumerate(lanes_to_use):
                adjusted_obstacle = obstacle_type.copy()
                adjusted_obstacle["speed"] *= (self.difficulty_multiplier * self.speed_multiplier)
                
                # Create the obstacle
                new_obstacle = Obstacle(lane, **adjusted_obstacle)
                
                # Adjust Y position for multi-obstacle formations
                if i > 0:
                    # Space out obstacles vertically when spawning multiple
                    new_obstacle.y -= min_spacing * i
                    new_obstacle.rect.y = new_obstacle.y
                    new_obstacle.collision_rect.y = new_obstacle.y + new_obstacle.hitbox_reduction
                
                # Add to tracking for valid paths
                self.obstacle_y_positions.append(new_obstacle.y)
                
                # Add the obstacle
                self.obstacles.append(new_obstacle)
    
    def spawn_multi_lane_pattern(self):
        """Create specific patterns of obstacles across multiple lanes based on level"""
        objects_level_int = int(self.objects_multiplier * 5) - 3  # Convert to -1 to 2 range
        
        if objects_level_int < 0 or random.random() > 0.15 * (objects_level_int + 1):
            # Don't spawn multi-lane pattern at lower levels or based on probability
            return False
            
        # Apply difficulty and speed multipliers to obstacle speed
        obstacle_type = random.choice(self.obstacle_configs["types"])
        adjusted_obstacle = obstacle_type.copy()
        adjusted_obstacle["speed"] *= (self.difficulty_multiplier * self.speed_multiplier)
        
        # Different pattern types
        pattern_type = random.randint(1, 4)
        
        if pattern_type == 1:
            # Wall: 2 obstacles side by side (never all 3 lanes)
            num_lanes = 2
            lanes_to_use = random.sample([0, 1, 2], num_lanes)
            
            # Verify this won't create impossible patterns
            if not self.ensure_valid_path(lanes_to_use, -60):
                return False
                
            for lane in lanes_to_use:
                new_obstacle = Obstacle(lane, **adjusted_obstacle)
                self.obstacles.append(new_obstacle)
                
        elif pattern_type == 2:
            # Zigzag pattern (modified to ensure passable)
            spacing = 120  # Increased spacing 
            lanes_to_include = []
            
            # Decide which lanes to include (always leave at least one free)
            max_lanes = 2 if objects_level_int < 2 else random.randint(1, 2)
            lanes_to_include = random.sample([0, 1, 2], max_lanes)
            
            for i, lane in enumerate(lanes_to_include):
                new_obstacle = Obstacle(lane, **adjusted_obstacle)
                # Stagger vertically based on lane number
                new_obstacle.y -= i * spacing  
                new_obstacle.rect.y = new_obstacle.y
                new_obstacle.collision_rect.y = new_obstacle.y + new_obstacle.hitbox_reduction
                self.obstacles.append(new_obstacle)
                    
        elif pattern_type == 3:
            # Alternating lanes
            avail_lanes = [0, 1, 2]
            lane1 = random.choice(avail_lanes)
            avail_lanes.remove(lane1)
            lane2 = random.choice(avail_lanes)
            
            spacing = 100 + random.randint(20, 60)  # Increased spacing for safety
            
            # First obstacle
            obstacle1 = Obstacle(lane1, **adjusted_obstacle)
            self.obstacles.append(obstacle1)
            
            # Second obstacle, offset vertically
            obstacle2 = Obstacle(lane2, **adjusted_obstacle)
            obstacle2.y -= spacing
            obstacle2.rect.y = obstacle2.y
            obstacle2.collision_rect.y = obstacle2.y + obstacle2.hitbox_reduction
            self.obstacles.append(obstacle2)
            
            # Only add a third obstacle if we have a high difficulty AND it won't block all paths
            if objects_level_int > 0 and random.random() < 0.3:
                # For third obstacle, explicitly choose a lane that creates a valid path
                avail_lanes = [0, 1, 2]
                avail_lanes.remove(lane1)
                if lane2 in avail_lanes:
                    avail_lanes.remove(lane2)
                
                if avail_lanes:  # Only add if there's a safe lane available
                    lane3 = random.choice(avail_lanes)
                    obstacle3 = Obstacle(lane3, **adjusted_obstacle)
                    obstacle3.y -= spacing * 2
                    obstacle3.rect.y = obstacle3.y
                    obstacle3.collision_rect.y = obstacle3.y + obstacle3.hitbox_reduction
                    self.obstacles.append(obstacle3)
                
        elif pattern_type == 4 and objects_level_int > 0:
            # Mixed jump/duck pattern - these are already passable by definition
            jump_duck = [
                {"obstacle_type": "jump", "lane": random.randint(0, 2)},
                {"obstacle_type": "duck", "lane": random.randint(0, 2)}
            ]
            
            spacing = 150  # Increased spacing
            
            for i, config in enumerate(jump_duck):
                # Copy and update obstacle config
                obs_config = adjusted_obstacle.copy()
                obs_config["obstacle_type"] = config["obstacle_type"]
                
                # Create obstacle
                new_obstacle = Obstacle(config["lane"], **obs_config)
                
                # Adjust position for second obstacle
                if i > 0:
                    new_obstacle.y -= spacing
                    new_obstacle.rect.y = new_obstacle.y
                    new_obstacle.collision_rect.y = new_obstacle.y + new_obstacle.hitbox_reduction
                
                self.obstacles.append(new_obstacle)
        
        return True
    
    def check_for_impossible_patterns(self):
        """Scan obstacles and remove any that would create impossible situations"""
        if not self.obstacles:
            return
            
        # Group obstacles by their approximate y-position
        obstacles_by_y = {}
        for obstacle in self.obstacles:
            y_key = obstacle.y // 20 * 20
            if y_key not in obstacles_by_y:
                obstacles_by_y[y_key] = []
            obstacles_by_y[y_key].append(obstacle)
            
        # Check for rows with obstacles in all 3 lanes
        obstacles_to_remove = []
        for y_key, obs_list in obstacles_by_y.items():
            lanes_covered = set(obs.lane for obs in obs_list)
            if len(lanes_covered) == 3:
                # Too many obstacles at this y position! Remove one
                obstacles_to_remove.append(random.choice(obs_list))
                
        # Remove problematic obstacles
        for obstacle in obstacles_to_remove:
            if obstacle in self.obstacles:
                self.obstacles.remove(obstacle)
    
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
        self.distance += 0.1 * delta_time * self.difficulty_multiplier * self.speed_multiplier
        
        # Spawn obstacles - adjust spawn rate based on objects multiplier
        self.spawn_timer += delta_time
        spawn_threshold = (self.spawn_rate / self.difficulty_multiplier) / self.objects_multiplier
        if self.spawn_timer > spawn_threshold:
            # Attempt to spawn multi-lane pattern first (for higher levels)
            if not self.spawn_multi_lane_pattern():
                # If no pattern was spawned, spawn regular obstacles
                self.spawn_obstacle()
            self.spawn_timer = 0
        
        # Move obstacles
        for obstacle in self.obstacles:
            obstacle.move(delta_time)
        
        # Check for and fix impossible patterns
        self.check_for_impossible_patterns()
        
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
        
        # Display difficulty and settings
        difficulty_text = font.render(
            f"Difficulty: {self.difficulty_multiplier:.1f}x", True, WHITE
        )
        screen.blit(difficulty_text, (screen.get_width() - 200, 10))
        
        # Display speed and objects multipliers
        speed_text = font.render(f"Speed: {self.speed_multiplier:.1f}x", True, WHITE)
        screen.blit(speed_text, (screen.get_width() - 200, 50))
        
        objects_text = font.render(f"Objects: {self.objects_multiplier:.1f}x", True, WHITE)
        screen.blit(objects_text, (screen.get_width() - 200, 90))
        
        # Display best score (moved to bottom)
        if self.best_score > 0:
            best_score_text = font.render(f"Best: {self.best_score}", True, WHITE)
            screen.blit(best_score_text, (screen.get_width() - 400, 50))
    
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
        self.obstacle_y_positions = [] 