import cv2
import mediapipe as mp
import numpy as np
import time
from typing import Optional, Callable, Dict, Any
from config import MovementConfig
from movement_analyzer import MovementAnalyzer

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

class MovementDetector:
    """Main class for movement detection using camera input"""
    
    def __init__(self, config: Optional[MovementConfig] = None, useCamera: bool = True, isTest: bool = False, callback: Optional[Callable[[str, Dict[str, Any]], None]] = None, debug: bool = False):
        self.config = config or MovementConfig()
        self.pose_detector = PoseDetector(self.config)
        self.movement_analyzer = MovementAnalyzer(self.config, self.pose_detector.mp_pose, debug)
        self.frame_counter = 0
        self.useCamera = useCamera
        self.isTest = isTest
        self.callback = callback
        self.debug = debug
        # For FPS calculation
        self.prev_frame_time = 0
        self.curr_frame_time = 0
        self.current_fps = 30.0  # Default FPS

    def process_movement(self, movement: str, data: Dict[str, Any]) -> None:
        """Call the callback function with detected movement"""
        print(f" ********** Movement detected: {movement} ********** ")
        if self.callback:
            self.callback(movement, data)
            
    def start_camera(self, video_path: Optional[str] = None) -> None:
        """Start processing video input for movement detection"""
        print("start_camera")
        if self.useCamera:
            cap = cv2.VideoCapture(self.config.camera_index)  # Use camera with index from config
            if not cap.isOpened():
                raise ValueError(f"Could not open camera with index {self.config.camera_index}")
            print(f"Camera {self.config.camera_index} opened successfully!")
        else:
            if video_path is None:
                raise ValueError("Video path must be provided when not using camera")
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Could not open video file: {video_path}")
            
            print(f"Video opened successfully!")
        
        print("Processing video for movement detection...")
        
        last_log_time = 0
        log_interval = 0.1  # Log every 100 milliseconds
        
        try:
            while True:
                # Calculate FPS
                self.curr_frame_time = time.time()
                fps = 1 / (self.curr_frame_time - self.prev_frame_time) if self.prev_frame_time > 0 else 30.0
                self.prev_frame_time = self.curr_frame_time
                
                # Update current FPS with smoothing
                self.current_fps = 0.9 * self.current_fps + 0.1 * fps  # Exponential moving average for stability
                
                # Pass the FPS to movement analyzer
                self.movement_analyzer.update_fps(self.current_fps)
                
                ret, image = cap.read()
                
                if not ret:
                    if not self.useCamera and cap.get(cv2.CAP_PROP_POS_FRAMES) >= total_frames:
                        print("End of video reached")
                        break
                    else:
                        print("Error reading frame, continuing...")
                        continue
                
                image = cv2.flip(image, 1)
                
                height, width = image.shape[:2]
                new_width = 500
                new_height = int(height * (new_width / width))
                image = cv2.resize(image, (new_width, new_height))
                
                landmarks = self.pose_detector.process_frame(image)
                
                if landmarks:
                    self.pose_detector.draw_landmarks(image, landmarks)
                    movement = self.movement_analyzer.detect_movement(landmarks)
                    if movement:
                        self.process_movement(movement, {"frame": self.frame_counter})
                else:
                    if self.frame_counter % 30 == 0:
                        print("No pose landmarks detected. Make sure your full body is visible.")
                
                # Calculate and display FPS only when using camera
                if self.useCamera:
                    fps_text = f"FPS: {self.current_fps:.1f}"
                    cv2.putText(image, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                
                if not self.isTest:
                    cv2.imshow('Movement Detection', image)
                    
                    if self.useCamera:
                        key = cv2.waitKey(1) & 0xFF
                        if key == 27:  # ESC key
                            print("Camera feed interrupted by user")
                            break
                    else:
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