import cv2
import mediapipe as mp
import numpy as np
from typing import Optional
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
    
    def __init__(self, config: Optional[MovementConfig] = None, useCamera: bool = True, isTest: bool = False, moves: any = None, debug: bool = False):
        self.config = config or MovementConfig()
        self.pose_detector = PoseDetector(self.config)
        self.movement_analyzer = MovementAnalyzer(self.config, self.pose_detector.mp_pose, debug)
        self.frame_counter = 0
        self.useCamera = useCamera
        self.isTest = isTest
        self.moves = moves
        self.debug = debug

    def process_movement(self, movement: str, data: any) -> None:
        """Log detected movement to console"""
        print(f" ********** Movement detected: {movement} ********** ")
        if movement == "Step Right":
            self.moves["right_move"](data)
        elif movement == "Step Left":
            self.moves["left_move"](data)
            
    def start_camera(self, video_path: Optional[str] = None) -> None:
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
                ret, image = cap.read()
                
                if not ret:
                    if not self.useCamera and cap.get(cv2.CAP_PROP_POS_FRAMES) >= total_frames:
                        print("End of video reached")
                        break
                    else:
                        print("Error reading frame, continuing...")
                        continue
                
                if not self.useCamera:
                    current_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
                    current_time = current_frame / fps
                    
                    if current_time - last_log_time >= log_interval:
                        if landmarks:
                            nose = landmarks.landmark[self.pose_detector.mp_pose.PoseLandmark.NOSE]
                            left_hip = landmarks.landmark[self.pose_detector.mp_pose.PoseLandmark.LEFT_HIP]
                        last_log_time = current_time
                
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