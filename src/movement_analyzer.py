import numpy as np
import time
from typing import Optional, List, Tuple
import mediapipe as mp
from config import MovementConfig

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

        self.x_coordinate_index = 0
        self.y_coordinate_index = 1
        self.z_coordinate_index = 2

        
        
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
                print(f"[DEBUG] {counter_name.title()} stability counter: {counter}/{self.config.required_stable_frames}")
            
            is_stable = counter >= self.config.required_stable_frames
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
            self.stable_counter = self.config.required_stable_frames
        else:
            self.stable_counter = 0

        return self.is_stable
    
    def update_is_in_motion_step(self, left_foot_distance: float, left_foot_is_left: bool, right_foot_distance: float, right_foot_is_left: bool) -> None:
        # update step

        # Determine which stability criterion to use
        is_stable_step, stable_check = self._determine_stability_criterion(
            left_foot_distance, left_foot_is_left,
            right_foot_distance, right_foot_is_left
        )

        if self.debug:
            print(f"[DEBUG] {stable_check} - {is_stable_step}")
            
        # Check stability and motion states
        if is_stable_step:
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
        if not right_foot_is_left and right_foot_distance > self.config.step_threshold:
            if self.debug:
                print(f"[DEBUG] Step Right detected - Diff: {right_foot_distance:.4f}")
            movement = "Step Right"
            self._after_movement_detected(movement)
            return movement
        return None

    def _detect_step_left(self, left_foot_distance: float, left_foot_is_left: bool) -> Optional[str]:
        """Detect step left movement"""
        if left_foot_is_left and left_foot_distance > self.config.step_threshold:
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
        self.last_detection_time = time.time()
        if self.debug:
            print(f"[DEBUG] Movement detected: {movement}")

    def detect_movement(self, landmarks: mp.solutions.pose.PoseLandmark) -> Optional[str]:
        """Detect and return the type of movement"""
        if landmarks is None:
            return None
            
        landmark_points = np.array([[lm.x, lm.y, lm.z] for lm in landmarks.landmark])
        self.frame_counter += 1
        
        self.update_landmarks_history(landmark_points)
        self.update_is_stable(landmark_points)

        left_foot_distance, left_foot_is_left = self.get_points_distance(self.LEFT_FOOT_INDEX, self.x_coordinate_index)
        right_foot_distance, right_foot_is_left = self.get_points_distance(self.RIGHT_FOOT_INDEX, self.x_coordinate_index)
        
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