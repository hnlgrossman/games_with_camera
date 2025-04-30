import pygame
import sys
from constants import FPS, WIDTH, HEIGHT
try:
    from test import MovementDetector
    CAMERA_SUPPORT = True
except ImportError as e:
    print(f"Warning: Camera support disabled - {str(e)}")
    CAMERA_SUPPORT = False
import threading

class GameEngine:
    def __init__(self, screen, courses):
        self.screen = screen
        self.courses = courses
        self.current_course_index = 0
        self.current_course = courses[self.current_course_index]
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
        self.show_fps = False
        self.frame_times = []  # For FPS calculation
        self.frame_time_limit = 30  # Number of frames to average
        
        # Create fonts
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        
        # For smooth transitions between courses
        self.transitioning = False
        self.transition_alpha = 0
        self.transition_speed = 5
        self.next_course_index = None
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.paused:
                        self.paused = False
                    else:
                        self.paused = True
                elif event.key == pygame.K_c and not self.transitioning and not self.paused:
                    # Start course transition
                    self.next_course_index = (self.current_course_index + 1) % len(self.courses)
                    self.transitioning = True
                    self.transition_alpha = 0
                elif event.key == pygame.K_p:
                    self.current_course.toggle_pause()
                elif event.key == pygame.K_f:
                    self.show_fps = not self.show_fps
    
    def handle_player_input(self):
        if self.paused or self.transitioning or self.current_course.paused:
            return
            
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]:
            self.current_course.player.move_left()
                
        if keys[pygame.K_RIGHT]:
            self.current_course.player.move_right()
            
        if keys[pygame.K_UP]:
            self.current_course.player.jump()
            
        if keys[pygame.K_DOWN]:
            self.current_course.player.duck()
        else:
            # Release duck when down key is released
            self.current_course.player.release_duck()
    
    def get_input_from_camera(self):
        if not CAMERA_SUPPORT:
            print("Camera support is not available. Please install required dependencies.")
            return
            
        print("get_input_from_camera")
        def right_move():
            # trigger_right()
            print("right_move")
            self.current_course.player.move_right()


        def left_move():
            # trigger_left()
            print("left_move")
            self.current_course.player.move_left()


        moves = {"right_move": right_move, "left_move": left_move}
        # Example using video file
        detector_video = MovementDetector(useCamera=True)
        video_path = "moves_videos/test_1.mp4"
        # video_path = "moves_videos/step_left_right.mp4"
        # video_path = "moves_videos/weirdo.mp4"
        print("start")
        # detector_video.start_camera(video_path)
        camera_thread = threading.Thread(target=detector_video.start_camera, args=(video_path,moves))
        camera_thread.start()
        print("end")
    
    def update(self):
        # Record frame time for FPS calculation
        self.frame_times.append(self.clock.get_time())
        if len(self.frame_times) > self.frame_time_limit:
            self.frame_times.pop(0)
            
        if self.transitioning:
            self.update_transition()
        elif not self.paused:
            self.current_course.update()
            
            # Game over check
            if self.current_course.check_collision():
                print(f"💥 Collision! Game Over on {self.current_course.name}")
                
                # Flash the screen red
                overlay = pygame.Surface((WIDTH, HEIGHT))
                overlay.fill((255, 0, 0))
                overlay.set_alpha(100)  # Semi-transparent
                self.screen.blit(overlay, (0, 0))
                pygame.display.flip()
                
                pygame.time.wait(1000)
                # Reset the course
                self.current_course.reset()
    
    def update_transition(self):
        if self.transition_alpha < 255 and self.next_course_index is None:
            # Fade out
            self.transition_alpha += self.transition_speed
        elif self.transition_alpha >= 255 and self.next_course_index is not None:
            # Switch courses
            self.current_course_index = self.next_course_index
            self.current_course = self.courses[self.current_course_index]
            self.next_course_index = None
            print(f"Switched to: {self.current_course.name}")
        else:
            # Fade in
            self.transition_alpha -= self.transition_speed
            if self.transition_alpha <= 0:
                self.transitioning = False
                self.transition_alpha = 0
    
    def render(self):
        # Render the current course
        self.current_course.draw(self.screen)
        
        # Draw pause screen if paused
        if self.paused:
            self._draw_pause_screen()
        
        # Draw transition effect
        if self.transitioning:
            self._draw_transition()
        
        # Draw FPS counter if enabled
        if self.show_fps:
            self._draw_fps_counter()
        
        pygame.display.flip()
    
    def _draw_pause_screen(self):
        # Create a semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(150)  # Semi-transparent
        self.screen.blit(overlay, (0, 0))
        
        # Draw pause text
        pause_text = self.font.render("PAUSED", True, (255, 255, 255))
        text_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(pause_text, text_rect)
        
        # Draw instructions
        instructions = [
            "Press ESC to resume",
            "Press C to change course",
            "Press F to show/hide FPS",
            "Left/Right arrows to move",
            "UP arrow to jump over obstacles",
            "DOWN arrow to duck under obstacles"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, (200, 200, 200))
            self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + 40 + i * 30))
    
    def _draw_transition(self):
        # Draw a fading overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(self.transition_alpha)
        self.screen.blit(overlay, (0, 0))
        
        # Draw text if fully faded out
        if self.transition_alpha >= 200:
            next_course_name = self.courses[self.next_course_index].name if self.next_course_index is not None else ""
            if next_course_name:
                text = self.font.render(f"Loading {next_course_name}...", True, (255, 255, 255))
                text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                self.screen.blit(text, text_rect)
    
    def _draw_fps_counter(self):
        if not self.frame_times:
            return
            
        # Calculate average frame time and FPS
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        fps = 1000 / avg_frame_time if avg_frame_time > 0 else 0
        
        fps_text = self.small_font.render(f"FPS: {fps:.1f}", True, (255, 255, 255))
        self.screen.blit(fps_text, (WIDTH - fps_text.get_width() - 10, HEIGHT - fps_text.get_height() - 10))
    
    def run(self):
        self.get_input_from_camera()
        while self.running:
            self.handle_events()
            self.handle_player_input()
            self.update()
            self.render()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit() 