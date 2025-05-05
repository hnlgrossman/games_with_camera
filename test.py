import cv2
import mediapipe as mp
import numpy as np
import time
from typing import Optional, Tuple, List, Dict
from dataclasses import dataclass
from keyboard_triggers import trigger_up, trigger_down, trigger_left, trigger_right
import threading

@dataclass
class MovementConfig:
    """Configuration parameters for movement detection"""
    min_detection_confidence: float = 0.5
    min_tracking_confidence: float = 0.5
    required_stable_frames: int = 4
    jump_threshold: float = 0.025
    step_threshold: float = 0.02
    bend_threshold: float = 0.1
    cooldown_period: float = 1.0
    stability_threshold: float = 0.028

    num_frames_to_check: int = 5
    

class PoseDetector:
    """Handles MediaPipe pose detection and landmark processing"""
    
    def __init__(self, config: MovementConfig):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=config.min_detection_confidence,
            min_tracking_confidence=config.min_tracking_confidence
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
    def process_frame(self, image: np.ndarray) -> Optional[mp.solutions.pose.PoseLandmark]:
        """Process a single frame and return pose landmarks"""
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_image)
        return results.pose_landmarks
        
    def draw_landmarks(self, image: np.ndarray, landmarks: mp.solutions.pose.PoseLandmark) -> None:
        """Draw pose landmarks on the image"""
        self.mp_drawing.draw_landmarks(
            image, 
            landmarks, 
            self.mp_pose.POSE_CONNECTIONS
        )

class MovementAnalyzer:
    """Analyzes pose landmarks to detect specific movements"""
    
    def __init__(self, config: MovementConfig, mp_pose):
        self.config = config
        self.mp_pose = mp_pose
        self.stable_position: Optional[np.ndarray] = None
        self.prev_landmarks: List[Optional[np.ndarray]] = None

        self.stable_counter: int = 0
        self.stable_counter_left_foot: int = 0
        self.stable_counter_right_foot: int = 0

        self.base_height: Optional[float] = None
        self.base_hip_x: Optional[float] = None
        self.last_detection_time: float = 0
        self.frame_counter: int = 0

        self.is_left_foot_stable: bool = True
        self.is_right_foot_stable: bool = True
        self.is_stable: bool = True
        self.is_in_motion: bool = False
        
        # Motion tracking
        self.debug: bool = False  # Enable debug logging
        
    def update_location(self, landmarks: mp.solutions.pose.PoseLandmark, landmark_points: np.ndarray) -> None:
        """Update the reference position for movement detection"""
        self.stable_position = landmark_points
        self.base_height = landmarks.landmark[self.mp_pose.PoseLandmark.NOSE].y
        self.base_hip_x = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_HIP].x
        # if self.debug:
        #     print(f"[DEBUG] Updated reference position - Base hip X: {self.base_hip_x:.4f}")

    def get_points_distance(self, point_num: int, type_point_index: int) -> float:
        current_point = self.prev_landmarks[0][point_num][type_point_index]
        prev_point = self.prev_landmarks[self.config.num_frames_to_check - 1][point_num][type_point_index]
        is_left = current_point < prev_point
        return np.linalg.norm(current_point - prev_point), is_left
        
    def update_is_stable(self, landmark_points: np.ndarray) -> bool:
        """Check if the current position is stable based on both feet positions"""
        if self.prev_landmarks is None:
            self.prev_landmarks = [landmark_points] * self.config.num_frames_to_check
        else:
            self.prev_landmarks.insert(0, landmark_points)
            self.prev_landmarks.pop()
            
        # Calculate distance between current and previous positions for both feet
        left_foot_distance, _ = self.get_points_distance(32, 0)
        right_foot_distance, _ = self.get_points_distance(31, 0)
        
        if self.debug:
            print(f"Left foot distance: {left_foot_distance:.4f}, Right foot distance: {right_foot_distance:.4f}")
        
        # Check left foot stability
        if left_foot_distance < self.config.stability_threshold:
            self.stable_counter_left_foot += 1
            if self.debug:
                print(f"[DEBUG] Left foot stability counter: {self.stable_counter_left_foot}/{self.config.required_stable_frames}")
            self.is_left_foot_stable = self.stable_counter_left_foot >= self.config.required_stable_frames
        else:
            if self.debug and self.stable_counter_left_foot > 0:
                print(f"[DEBUG] Reset left foot stability counter. Distance: {left_foot_distance:.4f}")
            self.stable_counter_left_foot = 0
            self.is_left_foot_stable = False

        # Check right foot stability
        if right_foot_distance < self.config.stability_threshold:
            self.stable_counter_right_foot += 1
            if self.debug:
                print(f"[DEBUG] Right foot stability counter: {self.stable_counter_right_foot}/{self.config.required_stable_frames}")
            self.is_right_foot_stable = self.stable_counter_right_foot >= self.config.required_stable_frames
        else:
            if self.debug and self.stable_counter_right_foot > 0:
                print(f"[DEBUG] Reset right foot stability counter. Distance: {right_foot_distance:.4f}")
            self.stable_counter_right_foot = 0
            self.is_right_foot_stable = False

        # Overall stability requires both feet to be stable
        self.is_stable = self.is_left_foot_stable and self.is_right_foot_stable
        if self.is_stable:
            self.stable_counter = self.config.required_stable_frames
        else:
            self.stable_counter = 0

        return self.is_stable

    def detect_movement(self, landmarks: mp.solutions.pose.PoseLandmark) -> Optional[str]:
        """Detect and return the type of movement"""
        if landmarks is None:
            return None
            
        landmark_points = np.array([[lm.x, lm.y, lm.z] for lm in landmarks.landmark])
        current_time = time.time()
        self.frame_counter += 1
        
        self.update_is_stable(landmark_points)

        is_stable = self.is_stable
        stable_check = "is_stable"
        
        nose_ym, _ = self.get_points_distance(self.mp_pose.PoseLandmark.NOSE, 0)
        left_foot_distance, left_foot_is_left = self.get_points_distance(32, 0)
        right_foot_distance, right_foot_is_left = self.get_points_distance(31, 0)

        if(not right_foot_is_left and right_foot_distance > left_foot_distance):
            is_stable = self.is_right_foot_stable
            stable_check = "is_right_foot_stable"
        elif(left_foot_is_left and left_foot_distance > right_foot_distance):
            is_stable = self.is_left_foot_stable
            stable_check = "is_left_foot_stable"
        else:
            if(self.stable_counter_right_foot > self.stable_counter_left_foot):
                is_stable = self.is_right_foot_stable
                stable_check = "is_right_foot_stable"
            else:
                is_stable = self.is_left_foot_stable
                stable_check = "is_left_foot_stable"

        # Establish stable position if needed
        if self.debug:
            print(f"[DEBUG] {stable_check} - {is_stable}")
        if is_stable:
            # self.update_location(landmarks, landmark_points)
            if(self.is_in_motion):
                if self.debug:
                    print(f"[DEBUG] is_in_motion reseted !!!")
                self.is_in_motion = False
            return None
        
        if(self.is_in_motion):
            return None
            
        # Get current positions
        
        
        # Update motion tracking
        # self._update_motion_state(left_hip_x, current_time)
        
        # Check if base positions are initialized
        # if self.base_height is None or self.base_hip_x is None:
        #     return None
        
        # Jump detection
        # jump_diff = self.base_height - nose_y
        # if jump_diff > self.config.jump_threshold:
        #     self.last_detection_time = current_time
        #     return "Jump"
            
        # # Bend detection
        # bend_diff = nose_y - self.base_height
        # if bend_diff > self.config.bend_threshold:
        #     self.last_detection_time = current_time
        #     return "Bend"
            
        # Step detection with improved logic
        # step_right_diff = left_hip_x - self.base_hip_x
        # step_left_diff = self.base_hip_x - left_hip_x
        # print(f"step_right_diff: {step_right_diff:.4f}, step_left_diff: {step_left_diff:.4f}")
        
        # if self.debug and self.frame_counter % 5 == 0:  # Log every 5th frame
        #     print(f"[DEBUG] Step differences - Right: {step_right_diff:.4f}, Left: {step_left_diff:.4f}")
        #     print(f"[DEBUG] Step threshold: {self.config.step_threshold:.4f}")
        
        # Only detect step if we're not already in motion in that direction
        if self.debug:  # Log every 5th frame
            print(f"[DEBUG] Right foot distance: {right_foot_distance:.4f}, Threshold: {self.config.step_threshold:.4f}")
            print(f"[DEBUG] Left foot distance: {left_foot_distance:.4f}, Threshold: {self.config.step_threshold:.4f}")

        if not right_foot_is_left and right_foot_distance > self.config.step_threshold:
            if self.debug:
                print(f"[DEBUG] Step Right detected - Diff: {right_foot_distance:.4f}")
            return "Step Right"
        
        if left_foot_is_left and left_foot_distance > self.config.step_threshold:
            if self.debug:
                print(f"[DEBUG] Step Left detected - Diff: {left_foot_distance:.4f}")
            return "Step Left"
            
        return None

class MovementDetector:
    """Main class for movement detection using camera input"""
    
    def __init__(self, config: Optional[MovementConfig] = None, useCamera: bool = True):
        self.config = config or MovementConfig()
        self.pose_detector = PoseDetector(self.config)
        self.movement_analyzer = MovementAnalyzer(self.config, self.pose_detector.mp_pose)
        self.frame_counter = 0
        self.useCamera = useCamera
        
    def process_movement(self, movement: str, moves: any = None) -> None:
        """Log detected movement to console"""
        print(f" ********** Movement detected: {movement} ********** ")
        self.movement_analyzer.is_in_motion = True
        if movement == "Step Right":
            moves["right_move"]()
        elif movement == "Step Left":
            moves["left_move"]()
            
    def start_camera(self, video_path: Optional[str] = None, moves: any = None) -> None:
        """Start processing video input for movement detection"""
        print("start_camera")
        if self.useCamera:
            cap = cv2.VideoCapture(1)  # Use camera (device index 0)
            if not cap.isOpened():
                raise ValueError("Could not open camera")
            print("Camera opened successfully!")
        else:
            if video_path is None:
                raise ValueError("Video path must be provided when not using camera")
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Could not open video file: {video_path}")
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps
            
            print(f"Video opened successfully!")
            print(f"Video properties: {fps:.2f} FPS, {total_frames} frames, {duration:.2f} seconds")
        
        print("Processing video for movement detection...")
        
        last_log_time = 0
        log_interval = 0.1  # Log every 100 milliseconds
        
        try:
            while True:
                # Read a frame
                ret, image = cap.read()
                
                # If frame is not read correctly, check if we've reached the end
                if not ret:
                    if not self.useCamera and cap.get(cv2.CAP_PROP_POS_FRAMES) >= total_frames:
                        print("End of video reached")
                        break
                    else:
                        print("Error reading frame, continuing...")
                        continue
                
                # Calculate current time in video
                if not self.useCamera:
                    current_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
                    current_time = current_frame / fps
                    
                    # Log duration every 100 milliseconds
                    if current_time - last_log_time >= log_interval:
                        if landmarks:
                            nose = landmarks.landmark[self.pose_detector.mp_pose.PoseLandmark.NOSE]
                            left_hip = landmarks.landmark[self.pose_detector.mp_pose.PoseLandmark.LEFT_HIP]
                        last_log_time = current_time
                
                # Flip image horizontally for mirror effect
                image = cv2.flip(image, 1)
                
                # Resize frame to 500px width while maintaining aspect ratio
                height, width = image.shape[:2]
                new_width = 500
                new_height = int(height * (new_width / width))
                image = cv2.resize(image, (new_width, new_height))
                
                # Process frame
                landmarks = self.pose_detector.process_frame(image)
                
                if landmarks:
                    # Draw landmarks
                    self.pose_detector.draw_landmarks(image, landmarks)
                    
                    # Detect movement
                    movement = self.movement_analyzer.detect_movement(landmarks)
                    if movement:
                        # print(f"Movement detected: {movement}")
                        # moves = [];
                        self.process_movement(movement, moves)
                else:
                    if self.frame_counter % 30 == 0:
                        print("No pose landmarks detected. Make sure your full body is visible.")
                
                # Display frame
                cv2.imshow('Movement Detection', image)
                
                # Wait for key press - different behavior for camera vs video
                if self.useCamera:
                    # For camera: small delay and check for ESC key
                    key = cv2.waitKey(1) & 0xFF
                    if key == 27:  # ESC key
                        print("Camera feed interrupted by user")
                        break
                else:
                    # For video: wait for Enter key press
                    print("\nPress Enter to continue to next frame (or ESC to exit)...")
                    key = cv2.waitKey(0) & 0xFF
                    if key == 27:  # ESC key
                        print("Video playback interrupted by user")
                        break
                
                self.frame_counter += 1
                
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        finally:
            cap.release()
            cv2.destroyAllWindows()

if __name__ == "__main__":

    def right_move():
        # trigger_right()
        print("right_move")

    def left_move():
        # trigger_left()
        print("left_move")

    moves = {"right_move": right_move, "left_move": left_move}
    # Example using video file
    detector_video = MovementDetector(useCamera=True)
    video_path = "moves_videos/test_1.mp4"
    # video_path = "moves_videos/step_left_right.mp4"
    # video_path = "moves_videos/weirdo.mp4"
    # print("start")
    detector_video.start_camera(video_path, moves)
    # camera_thread = threading.Thread(target=detector_video.start_camera, args=(video_path,moves))
    # camera_thread.start()
    # print("end")
    # # Example using camera
    # # detector_camera = MovementDetector(useCamera=True)
    # # detector_camera.start_camera()  # No video path needed when using camera

    # # Wait for the camera thread to finish before exiting the main script
    # camera_thread.join()
    # print("Camera thread finished.") 