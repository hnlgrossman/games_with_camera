import numpy as np
import time
from typing import Optional, List, Tuple
import mediapipe as mp
from config import MovementConfig
from sound_manager import SoundManager

class MovementAnalyzer:
    """Analyzes pose landmarks to detect specific movements"""
    
    def __init__(self, config: MovementConfig, mp_pose, debug: bool = False):
        self.config = config
        self.mp_pose = mp_pose
        self.debug = debug
        
        # Landmark tracking
        self.stable_position: Optional[np.ndarray] = None
        self.prev_landmarks: List[Optional[np.ndarray]] = None
        self.frame_counter: int = 0
        
        # Reference points
        self.base_height: Optional[float] = None
        self.base_hip_x: Optional[float] = None
        
        # Stability counters
        self.stable_counter: int = 0
        self.stable_counter_left_foot: int = 0
        self.stable_counter_right_foot: int = 0
        
        # State flags
        self.is_left_foot_stable: bool = True
        self.is_right_foot_stable: bool = True
        self.is_stable: bool = True
        self.is_in_motion: dict = {"step": False, "jump": False, "bend": False}
        self.last_detection_time: float = 0
        
        # Landmark indices for common body parts
        self.LEFT_FOOT_INDEX = 32
        self.RIGHT_FOOT_INDEX = 31
        self.NOSE_INDEX = self.mp_pose.PoseLandmark.NOSE
        self.LEFT_HIP_INDEX = self.mp_pose.PoseLandmark.LEFT_HIP
        self.LEFT_KNEE_INDEX = self.mp_pose.PoseLandmark.LEFT_KNEE
        self.RIGHT_KNEE_INDEX = self.mp_pose.PoseLandmark.RIGHT_KNEE

        self.x_coordinate_index = 0
        self.y_coordinate_index = 1
        self.z_coordinate_index = 2

        self.is_current_step_stable = False
        
        # FPS adaptation
        self.current_fps = 30.0
        self.required_stable_frames = self.config.required_stable_frames_per_30_fps
        
        # Initialize sound manager only if sound is enabled
        self.sound_manager = None
        if self.config.sound_enabled:
            self.sound_manager = SoundManager(volume=self.config.sound_volume)
            if self.debug:
                print(f"[DEBUG] Sound manager initialized with volume {self.config.sound_volume}")
        elif self.debug:
            print("[DEBUG] Sound is disabled in config")
        
    def update_fps(self, fps: float) -> None:
        """Update the current FPS and adjust required_stable_frames accordingly"""
        self.current_fps = max(1.0, fps)  # Ensure FPS is at least 1 to avoid division by zero
        
        # Calculate the adjusted stable frames based on FPS ratio
        base_frames = self.config.required_stable_frames_per_30_fps
        fps_ratio = self.current_fps / 30.0
        
        # Scale the required frames proportionally to the FPS
        # Formula: required_frames = base_frames * (current_fps / 30)
        scaled_frames = base_frames * fps_ratio
        
        # Round to nearest integer and ensure minimum of 1 frame
        self.required_stable_frames = max(1, round(scaled_frames))
        
        if self.debug:
            print(f"[DEBUG] FPS: {self.current_fps:.1f}, FPS ratio: {fps_ratio:.2f}, Required stable frames: {self.required_stable_frames}")
        
    def update_location(self, landmarks: mp.solutions.pose.PoseLandmark, landmark_points: np.ndarray) -> None:
        """Update the reference position for movement detection"""
        self.stable_position = landmark_points
        self.base_height = landmarks.landmark[self.NOSE_INDEX].y
        self.base_hip_x = landmarks.landmark[self.LEFT_HIP_INDEX].x

    def get_points_distance(self, point_num: int, type_point_index: int) -> Tuple[float, bool]:
        """Calculate distance between current and previous positions of a landmark
        
        Args:
            point_num: Index of the landmark point
            type_point_index: Index for the coordinate (0=x, 1=y, 2=z)
            
        Returns:
            Tuple of (distance, is_left) where is_left indicates direction
        """
        current_point = self.prev_landmarks[0][point_num][type_point_index]
        prev_point = self.prev_landmarks[self.config.num_frames_to_check - 1][point_num][type_point_index]
        is_left = current_point < prev_point
        return np.linalg.norm(current_point - prev_point), is_left
    
    def update_landmarks_history(self, landmark_points: np.ndarray) -> None:
        """Maintain history of landmark points for movement detection"""
        if self.prev_landmarks is None:
            self.prev_landmarks = [landmark_points] * self.config.num_frames_to_check
        else:
            self.prev_landmarks.insert(0, landmark_points)
            self.prev_landmarks.pop()

    def _update_foot_stability(self, foot_distance: float, is_left_foot: bool) -> bool:
        """Update stability counter for a foot and return stability status
        
        Args:
            foot_distance: Distance the foot has moved
            is_left_foot: True if left foot, False if right foot
            
        Returns:
            Boolean indicating if the foot is stable
        """
        if is_left_foot:
            counter_name = "left foot"
            counter = self.stable_counter_left_foot
        else:
            counter_name = "right foot"
            counter = self.stable_counter_right_foot
            
        if foot_distance < self.config.stability_threshold:
            counter += 1
            if self.debug:
                print(f"[DEBUG] {counter_name.title()} stability counter: {counter}/{self.required_stable_frames}")
            
            is_stable = counter >= self.required_stable_frames
        else:
            if self.debug and counter > 0:
                print(f"[DEBUG] Reset {counter_name} stability counter. Distance: {foot_distance:.4f}")
            counter = 0
            is_stable = False
            
        # Update class variables
        if is_left_foot:
            self.stable_counter_left_foot = counter
            self.is_left_foot_stable = is_stable
        else:
            self.stable_counter_right_foot = counter
            self.is_right_foot_stable = is_stable
            
        return is_stable
        
    def update_is_stable(self, landmark_points: np.ndarray) -> bool:
        """Check if the current position is stable based on both feet positions"""
            
        left_foot_distance, _ = self.get_points_distance(self.LEFT_FOOT_INDEX, self.x_coordinate_index)
        right_foot_distance, _ = self.get_points_distance(self.RIGHT_FOOT_INDEX, self.x_coordinate_index)
        
        if self.debug:
            print(f"Left foot distance: {left_foot_distance:.4f}, Right foot distance: {right_foot_distance:.4f}")
        
        self._update_foot_stability(left_foot_distance, True)
        self._update_foot_stability(right_foot_distance, False)

        self.is_stable = self.is_left_foot_stable or self.is_right_foot_stable
        
        # Update overall stability counter
        if self.is_stable:
            self.stable_counter = self.required_stable_frames
        else:
            self.stable_counter = 0

        return self.is_stable
    
    def update_is_in_motion_step(self, left_foot_distance: float, left_foot_is_left: bool, right_foot_distance: float, right_foot_is_left: bool) -> None:
        # update step

        # Determine which stability criterion to use
        self.is_current_step_stable, stable_check = self._determine_stability_criterion(
            left_foot_distance, left_foot_is_left,
            right_foot_distance, right_foot_is_left
        )

        if self.debug:
            print(f"[DEBUG] {stable_check} - {self.is_current_step_stable}")
            
        # Check stability and motion states
        if self.is_current_step_stable:
            if self.is_in_motion["step"]:
                if self.debug:
                    print("[DEBUG] is_in_motion reset")
                self.is_in_motion["step"] = False
            return None

    def _determine_stability_criterion(self, left_foot_distance: float, left_foot_is_left: bool,
                                     right_foot_distance: float, right_foot_is_left: bool) -> Tuple[bool, str]:
        """Determine which stability criterion to use based on foot movements"""
        if not right_foot_is_left and right_foot_distance > left_foot_distance:
            return self.is_right_foot_stable, "is_right_foot_stable"
        elif left_foot_is_left and left_foot_distance > right_foot_distance:
            return self.is_left_foot_stable, "is_left_foot_stable"
        else:
            if self.stable_counter_right_foot > self.stable_counter_left_foot:
                return self.is_right_foot_stable, "is_right_foot_stable"
            else:
                return self.is_left_foot_stable, "is_left_foot_stable"

    def _detect_step_right(self, right_foot_distance: float, right_foot_is_left: bool) -> Optional[str]:
        """Detect step right movement"""
        if not self.is_current_step_stable and not right_foot_is_left and right_foot_distance > self.config.step_threshold:
            if self.debug:
                print(f"[DEBUG] Step Right detected - Diff: {right_foot_distance:.4f}")
            movement = "Step Right"
            self._after_movement_detected(movement)
            return movement
        return None

    def _detect_step_left(self, left_foot_distance: float, left_foot_is_left: bool) -> Optional[str]:
        """Detect step left movement"""
        if not self.is_current_step_stable and left_foot_is_left and left_foot_distance > self.config.step_threshold:
            if self.debug:
                print(f"[DEBUG] Step Left detected - Diff: {left_foot_distance:.4f}")
            movement = "Step Left"
            self._after_movement_detected(movement)
            return movement
        return None

    def _after_movement_detected(self, movement: str) -> None:
        """Handle common tasks after any movement is detected
        
        Args:
            movement: The detected movement type
        """
        if movement == "Step Right" or movement == "Step Left":
            self.is_in_motion["step"] = True
        elif movement == "Jump":
            self.is_in_motion["jump"] = True
        elif movement == "Bend":
            self.is_in_motion["bend"] = True
            
        # Play the movement sound if enabled
        if self.sound_manager is not None:
            self.sound_manager.play_movement_sound(movement)
            
        self.last_detection_time = time.time()
        if self.debug:
            print(f"[DEBUG] Movement detected: {movement}")

    def _are_required_landmarks_visible(self, landmarks) -> bool:
        """Check if all required landmarks are visible
        
        Args:
            landmarks: MediaPipe pose landmarks
            
        Returns:
            Boolean indicating if all required landmarks are visible and valid
        """
        required_landmarks = [
            self.NOSE_INDEX,
            self.LEFT_HIP_INDEX,
            self.LEFT_FOOT_INDEX,
            self.RIGHT_FOOT_INDEX,
            self.LEFT_KNEE_INDEX,
            self.RIGHT_KNEE_INDEX
        ]
        
        for landmark_idx in required_landmarks:
            if landmark_idx >= len(landmarks.landmark) or landmarks.landmark[landmark_idx].visibility < self.config.visibility_threshold:
                return False
        
        return True

    def detect_movement(self, landmarks: mp.solutions.pose.PoseLandmark) -> Optional[str]:
        """Detect and return the type of movement"""
        if landmarks is None:
            return None
            
        # Check if all required landmarks are visible
        if not self._are_required_landmarks_visible(landmarks):
            return None
            
        landmark_points = np.array([[lm.x, lm.y, lm.z] for lm in landmarks.landmark])
        self.frame_counter += 1
        
        self.update_landmarks_history(landmark_points)
        self.update_is_stable(landmark_points)

        left_foot_distance, left_foot_is_left = self.get_points_distance(self.LEFT_FOOT_INDEX, self.x_coordinate_index)
        right_foot_distance, right_foot_is_left = self.get_points_distance(self.RIGHT_FOOT_INDEX, self.x_coordinate_index)
        
        # Debug logs for nose and knees positions
        if self.debug:
            nose = landmarks.landmark[self.NOSE_INDEX]
            left_knee = landmarks.landmark[self.LEFT_KNEE_INDEX]
            right_knee = landmarks.landmark[self.RIGHT_KNEE_INDEX]
            print(f"[DEBUG] Nose position: x={nose.x:.4f}, y={nose.y:.4f}, z={nose.z:.4f}, visibility={nose.visibility:.2f}")
            print(f"[DEBUG] Left knee: x={left_knee.x:.4f}, y={left_knee.y:.4f}, z={left_knee.z:.4f}, visibility={left_knee.visibility:.2f}")
            print(f"[DEBUG] Right knee: x={right_knee.x:.4f}, y={right_knee.y:.4f}, z={right_knee.z:.4f}, visibility={right_knee.visibility:.2f}")
        
        self.update_is_in_motion_step(left_foot_distance, left_foot_is_left, right_foot_distance, right_foot_is_left)

        # Debug output for foot distances
        if self.debug:
            print(f"[DEBUG] Right foot distance: {right_foot_distance:.4f}, Threshold: {self.config.step_threshold:.4f}")
            print(f"[DEBUG] Left foot distance: {left_foot_distance:.4f}, Threshold: {self.config.step_threshold:.4f}")

        # Check if any motion is in progress
        if any(self.is_in_motion.values()):
            return None

        # Detect steps using dedicated functions
        movement = self._detect_step_right(right_foot_distance, right_foot_is_left)
        if movement:
            return movement
            
        movement = self._detect_step_left(left_foot_distance, left_foot_is_left)
        if movement:
            return movement
            
        return None