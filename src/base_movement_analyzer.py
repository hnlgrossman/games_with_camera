import numpy as np
import time
import logging
from typing import Optional, List, Tuple, Dict, Any
import mediapipe as mp
from sound_manager import SoundManager


from src.constants import (
    LEFT_FOOT_INDEX, RIGHT_FOOT_INDEX, NOSE_INDEX, 
    LEFT_KNEE_INDEX, RIGHT_KNEE_INDEX,
    LEFT_SHOULDER_INDEX, RIGHT_SHOULDER_INDEX,
    X_COORDINATE_INDEX, Y_COORDINATE_INDEX, Z_COORDINATE_INDEX,
    LEFT_HIP_INDEX, RIGHT_HIP_INDEX,
    LEFT_HEEL_INDEX, RIGHT_HEEL_INDEX
)

class BaseMovementAnalyzer:
    """Base class for movement analysis that provides core functionality to detect movements from pose landmarks"""
    
    def __init__(self, config: Any, mp_pose, debug: bool = False):
        self.config = config
        self.mp_pose = mp_pose
        self.debug = debug
        
        # Set up logging
        self.logger = logging.getLogger(self.__class__.__name__)

        self.current_landmark_points = None
        
        # Landmark tracking
        self.stable_position: Optional[np.ndarray] = None
        self.prev_landmarks: List[Optional[np.ndarray]] = None
        self.frame_counter: int = 0
        
        # Reference points
        self.base_height: Optional[float] = None
        self.base_hip_x: Optional[float] = None

        # Timestamp for last detection
        self.last_detection_time: float = 0
        
        # Points distance tracking dictionary
        self.points_distance = {
            LEFT_FOOT_INDEX: [{}, {}, {}],
            RIGHT_FOOT_INDEX: [{}, {}, {}],
            NOSE_INDEX: [{}, {}, {}],
            LEFT_SHOULDER_INDEX: [{}, {}, {}],
            RIGHT_SHOULDER_INDEX: [{}, {}, {}],
            RIGHT_HIP_INDEX: [{}, {}, {}],
            LEFT_HIP_INDEX: [{}, {}, {}],
            LEFT_HEEL_INDEX: [{}, {}, {}],
            RIGHT_HEEL_INDEX: [{}, {}, {}],
        }

        self.movement_type_map: Dict[str, Any] = {}

        # FPS adaptation
        self.current_fps = 30.0
        self.num_frames_to_check = self.config.num_frames_to_check_per_30_fps
        
        # Movement detectors will be initialized in child classes
        self.movement_detectors = []
        
        # Sound manager will be initialized in child classes if needed
        self.sound_manager = None
        if self.config.sound_enabled:
            self.sound_manager = SoundManager(volume=self.config.sound_volume)
            if self.debug:
                self.logger.debug(f"Sound manager initialized with volume {self.config.sound_volume}")
        elif self.debug:
            self.logger.debug("Sound is disabled in config")
        
    def update_fps(self, fps: float) -> None:
        self.current_fps = max(1.0, fps)  # Ensure FPS is at least 1 to avoid division by zero

    def get_per_30_fps(self, value: int, min_value: int = 2) -> int:
        """Get the value per 30 FPS"""
        fps_ratio = self.current_fps / 30.0
        return max(min_value, round(value * fps_ratio))

    def get_points_distance(self, point_num: int, type_point_index: int) -> Tuple[float, bool]:
        """Get the distance and direction of a point's movement"""
        return self.points_distance[point_num][type_point_index]["points"], self.points_distance[point_num][type_point_index]["is_position_smaller"]
    
    def update_landmarks_history(self, landmark_points: np.ndarray) -> None:
        """Maintain history of landmark points for movement detection"""
        if self.prev_landmarks is None:
            # Initialize with copies of the first landmark_points
            self.prev_landmarks = [np.copy(landmark_points) for _ in range(self.num_frames_to_check)]
        else:
            self.prev_landmarks.insert(0, landmark_points)
            self.prev_landmarks.pop()
    
    def map_points_distance(self) -> None:
        """Map the points distance to the points_distance dictionary"""
        for point_index, coordinates in self.points_distance.items():
            for i in range(3):
                current_point = self.prev_landmarks[0][point_index][i]
                prev_point = self.prev_landmarks[self.num_frames_to_check - 1][point_index][i]
                is_position_smaller = current_point < prev_point
                coordinates[i]["points"] = round(abs(current_point - prev_point), 3)
                coordinates[i]["is_position_smaller"] = is_position_smaller

    def update_is_stable_general(self) -> bool:
        """
        Check if the current position is stable based on movement detectors.
        This method is kept for backward compatibility but now relies on 
        the movement detectors' stability status.
        """
        # Update each movement detector's stability
        for detector in self.movement_detectors:
            detector.update_stability_and_motion_status()
        
    def _update_fps_dependent_values(self) -> None:
        """Update FPS-dependent values based on current FPS"""
        self.num_frames_to_check = self.get_per_30_fps(self.config.num_frames_to_check_per_30_fps)

    def _are_required_landmarks_visible(self, landmarks) -> bool:
        """Check if all required landmarks are visible
        
        Args:
            landmarks: MediaPipe pose landmarks
            
        Returns:
            Boolean indicating if all required landmarks are visible and valid
        """
        required_landmarks = [
            NOSE_INDEX,
            LEFT_HIP_INDEX,
            RIGHT_HIP_INDEX,
            LEFT_FOOT_INDEX,
            RIGHT_FOOT_INDEX,
            LEFT_KNEE_INDEX,
            RIGHT_KNEE_INDEX,
            LEFT_SHOULDER_INDEX,
            RIGHT_SHOULDER_INDEX
        ]
        
        for landmark_idx in required_landmarks:
            if landmark_idx >= len(landmarks.landmark) or landmarks.landmark[landmark_idx].visibility < self.config.visibility_threshold:
                return False
        
        return True

    def _map_movement_types(self) -> None:
        """Map movement types to their detectors for fast lookup"""
        for movement_type in self.movement_detectors:
            if detect_moves := movement_type.detectable_moves:
                for move in detect_moves:
                    self.movement_type_map[move] = movement_type

    def _after_movement_detected(self, movement: str) -> None:
        """Handle common tasks after any movement is detected
        
        Args:
            movement: The detected movement type
        """
        # Inform the appropriate movement detector that its movement was detected
        if movement in self.movement_type_map:
            self.movement_type_map[movement].on_movement_detected()
        
        # Play the movement sound if enabled and sound manager exists
        if self.sound_manager is not None:
            self.sound_manager.play_movement_sound(movement)
            
        self.last_detection_time = time.time()
        if self.debug:
            self.logger.debug(f"Movement detected: {movement}")

    def map_core_data(self, landmark_points) -> Optional[str]:
        self.current_landmark_points = landmark_points
        self._update_fps_dependent_values()
        
        self._map_movement_types()
        self.update_landmarks_history(landmark_points)
        
        self.map_points_distance()
        
        

    def update_before_detect(self, landmark_points) -> Optional[str]:
        self.update_is_stable_general()
        pass

    def detect_movement(self) -> Optional[str]:
        # Check if any detector is already in motion
        if not self.config.allow_multiple_movements and any(detector.is_in_motion for detector in self.movement_detectors):
            if self.debug:
                self.logger.debug(f"Movement already in motion, skipping detection because of {[detector.name for detector in self.movement_detectors if detector.is_in_motion]}")
            return None

        # Try to detect movements using specialized detectors
        for detector in self.movement_detectors:
            if detected := detector.detect():
                self._after_movement_detected(detected)
                return detected
            
        return None
    

    def check_for_movment(self, landmarks: mp.solutions.pose.PoseLandmark):
        """Detect and return the type of movement"""
        if landmarks is None:
            return None
            
        # Check if all required landmarks are visible
        if not self._are_required_landmarks_visible(landmarks):
            if self.debug:
                self.logger.debug("Required landmarks not visible, cannot detect movement or set base height.")
            return None
            
        landmark_points = np.array([[lm.x, lm.y, lm.z] for lm in landmarks.landmark])
        self.frame_counter += 1

        self.map_core_data(landmark_points)

        self.update_before_detect(landmark_points)
        self._log_debug_info()

        detect_movement = self.detect_movement()

        return detect_movement
    
    def process_frame(self, frame):
        return frame
    
    def _log_debug_info(self):
        pass
    