import cv2
import mediapipe as mp
import numpy as np
import time
import logging
from typing import Optional, Callable, Dict, Any
from config import MovementConfig
from movement_analyzer import MovementAnalyzer
from logger import setup_logging

class PoseDetector:
    """Handles MediaPipe pose detection and landmark processing"""
    
    def __init__(self, config: MovementConfig):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=config.min_detection_confidence,
            min_tracking_confidence=config.min_tracking_confidence,
            model_complexity=0,  # Use lightweight model for better performance
            # static_image_mode=False,  # Set to False for video processing
            # smooth_landmarks=True  # Enable landmark smoothing for better performance
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
    def process_frame(self, image: np.ndarray) -> Optional[mp.solutions.pose.PoseLandmark]:
        """Process a single frame and return pose landmarks"""
        # resized_frame = cv2.resize(image, (480, 320))

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

        # Draw blue circles for specific landmarks (e.g., hands or feet)
        # Landmark indices for feet are typically 31 (RIGHT_FOOT_INDEX) and 32 (LEFT_FOOT_INDEX)
        # You might need to confirm these specific indices based on MediaPipe's documentation
        # for the exact body parts you want to highlight.
        # if landmarks:
        #     image_height, image_width, _ = image.shape
        #     for idx, landmark in enumerate(landmarks.landmark):
        #         if idx == 31 or idx == 32:  # Example: LEFT_FOOT_INDEX and RIGHT_FOOT_INDEX
        #             # Convert normalized landmark coordinates to pixel coordinates
        #             cx, cy = int(landmark.x * image_width), int(landmark.y * image_height)
        #             # Draw a blue circle
        #             cv2.circle(image, (cx, cy), 10, (255, 0, 0), -1)  # Blue color in BGR

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
        self.prev_frame_time = 0.0 # Initialize as float
        self.curr_frame_time = 0.0 # Initialize as float
        self.current_fps = 30.0  # Default FPS, will be overridden by video's actual FPS if applicable
        self.last_fps_print_time = 0.0  # Track when we last printed FPS
        
        # Get logger instance. Configuration is handled by setup_logging in main.py
        self.logger = logging.getLogger('MovementDetector')
        self.logger.info(f"MovementDetector initialized. Debug mode: {self.debug}")
        self.logger.debug("This is a DEBUG message from MovementDetector.")

    def process_movement(self, movement: str, data: Dict[str, Any]) -> None:
        """Call the callback function with detected movement"""
        self.logger.info(f"Movement detected: {movement}, Data: {data}")
        if self.callback:
            self.callback(movement, data)
            
    def start_camera(self, video_path: Optional[str] = None) -> None:
        """Start processing video input for movement detection"""
        self.logger.info("Starting camera/video processing")
        
        total_frames = 0 

        if self.useCamera:
            cap = cv2.VideoCapture(self.config.camera_index)  # Use camera with index from config
            if not cap.isOpened():
                error_msg = f"Could not open camera with index {self.config.camera_index}"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
            self.logger.info(f"Camera {self.config.camera_index} opened successfully!")
            # For camera, self.current_fps is initialized to 30.0 and will be dynamically calculated.
            # self.prev_frame_time is initialized to 0.0, will be set in the loop.
        else: # Processing a video file
            if video_path is None:
                error_msg = "Video path must be provided when not using camera"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                error_msg = f"Could not open video file: {video_path}"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Get original FPS from video
            original_fps = cap.get(cv2.CAP_PROP_FPS)
            print(f"Original FPS: {original_fps}")
            if original_fps <= 0: 
                self.logger.warning(f"Could not get valid FPS from video {video_path}. Defaulting to 30.0 FPS.")
                self.current_fps = 30.0 
            else:
                self.current_fps = original_fps
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.logger.info(f"Video opened successfully! Original FPS: {self.current_fps:.2f}, Total Frames: {total_frames}")
        
        self.logger.info("Processing video for movement detection...")
        
        # For periodic prompting when video is paused using waitKey(0)
        last_prompt_time = time.time()
        prompt_interval_seconds = 5.0
        
        try:
            while True:
                if self.useCamera:
                    # Calculate FPS dynamically for camera
                    self.curr_frame_time = time.time()
                    if self.prev_frame_time > 0: # Ensure prev_frame_time is set (i.e., not the first frame)
                        time_diff = self.curr_frame_time - self.prev_frame_time
                        if time_diff > 0: # Avoid division by zero or negative time difference
                            fps = 1.0 / time_diff
                        else:
                            fps = self.current_fps # Maintain current FPS if time_diff is not positive
                    else: # First frame for camera, or if prev_frame_time was not set
                        fps = self.current_fps # Use initial default (e.g., 30 FPS) or current smoothed FPS
                    
                    self.prev_frame_time = self.curr_frame_time # Update for next iteration
                    
                    # Update current FPS with smoothing
                    self.current_fps = 0.9 * self.current_fps + 0.1 * fps  # Exponential moving average for stability
                # else for video, self.current_fps is already set to original_fps and remains constant.
                
                # Pass the FPS to movement analyzer
                # self.movement_analyzer.update_fps(self.current_fps)
                
                ret, image = cap.read()
                
                if not ret:
                    # Check if it's the end of the video file
                    if not self.useCamera and total_frames > 0 and cap.get(cv2.CAP_PROP_POS_FRAMES) >= total_frames:
                        self.logger.info("End of video reached")
                        break
                    else: # Could be an actual read error or end of a stream
                        self.logger.warning("Error reading frame or end of stream reached.")
                        if not self.useCamera: # If it's a video file and frame read failed, assume end or unrecoverable error
                            self.logger.info("Stopping video processing due to frame read error or end of video.")
                            break 
                        continue # For camera, continue trying to read frames
                
                image = cv2.flip(image, 1)
                
                height, width = image.shape[:2]
                new_width = 500
                new_height = int(height * (new_width / width))
                image = cv2.resize(image, (new_width, new_height))
                
                landmarks = self.pose_detector.process_frame(image)
                
                if landmarks:
                    self.pose_detector.draw_landmarks(image, landmarks)
                    # start_time = time.time()
                    movement = self.movement_analyzer.detect_movement(landmarks)
                    # end_time = time.time()
                    # print(f"Movement detection took: {(end_time - start_time) * 1000:.2f} ms")
                    if movement:
                        self.process_movement(movement, {"frame": self.frame_counter, "fps": round(self.current_fps, 1)})
                else:
                    if self.frame_counter % 30 == 0: # Log every 30 frames
                        self.logger.warning("No pose landmarks detected. Make sure your full body is visible.")
                
                # Display FPS on the image
                fps_text = f"FPS: {self.current_fps:.1f}"
                cv2.putText(image, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                
                # Print FPS to console once per second
                if time.time() - self.last_fps_print_time >= 1.0:
                    # print(f"Current FPS: {self.current_fps:.1f}")
                    self.last_fps_print_time = time.time()
                
                
                if not self.isTest:
                    cv2.imshow('Movement Detection', image)
                    
                    key_wait_duration = 1 # Default for camera, non-blocking
                    if not self.useCamera: # If it's a video
                        key_wait_duration = 0 # Wait indefinitely for a key, allowing frame-by-frame stepping
                        
                        # If waiting indefinitely, periodically prompt the user
                        current_time_for_prompt = time.time()
                        if current_time_for_prompt - last_prompt_time > prompt_interval_seconds:
                             self.logger.info("Video paused. Press any key to advance to the next frame, or ESC to exit.")
                             last_prompt_time = current_time_for_prompt
                    
                    key = cv2.waitKey(key_wait_duration) & 0xFF
                    if key == 27:  # ESC key
                        self.logger.info("Processing interrupted by user (ESC pressed).")
                        break
                
                self.frame_counter += 1
                                # Measure overall iteration time
                # iteration_end_time = time.time()
                # print(f"Full frame processing took: {(iteration_end_time - self.curr_frame_time) * 1000:.2f} ms")

                if self.debug:
                    self.logger.debug(f"Frame {self.frame_counter} processed ****************\n")
                
        except Exception as e:
            print(f"An error occurred during processing: {str(e)}")
            self.logger.error(f"An error occurred during processing: {str(e)}", exc_info=True)
        finally:
            self.logger.info("Releasing video capture and destroying OpenCV windows.")
            cap.release()
            cv2.destroyAllWindows() 