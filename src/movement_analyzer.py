import numpy as np
import time
import logging
from typing import Optional, List, Tuple, Dict
import mediapipe as mp
from config import MovementConfig
from sound_manager import SoundManager
from src.movements.step_movement import StepMovement
from src.movements.jump_movement import JumpMovement
from src.movements.bend_movement import BendMovement
from src.movements.base_movement import BaseMovement
from src.constants import (
    LEFT_FOOT_INDEX, RIGHT_FOOT_INDEX, NOSE_INDEX, 
    LEFT_KNEE_INDEX, RIGHT_KNEE_INDEX,
    LEFT_SHOULDER_INDEX, RIGHT_SHOULDER_INDEX,
    X_COORDINATE_INDEX, Y_COORDINATE_INDEX, Z_COORDINATE_INDEX,
    LEFT_HIP_INDEX, RIGHT_HIP_INDEX
)

class MovementAnalyzer:
    """Analyzes pose landmarks to detect specific movements"""
    
    def __init__(self, config: MovementConfig, mp_pose, debug: bool = False):
        self.config = config
        self.mp_pose = mp_pose
        self.debug = debug
        
        # Set up logging
        self.logger = logging.getLogger('MovementAnalyzer')
        
        # Landmark tracking
        self.stable_position: Optional[np.ndarray] = None
        self.prev_landmarks: List[Optional[np.ndarray]] = None
        self.frame_counter: int = 0
        
        # Reference points
        self.base_height: Optional[float] = None
        self.base_hip_x: Optional[float] = None
        
        # Stability counter for overall stability
        self.stable_counter: int = 0
        self.is_stable: bool = True

        # Timestamp for last detection
        self.last_detection_time: float = 0
        
        # Use imported constants directly without reassignment
        
        self.points_distance = {
            LEFT_FOOT_INDEX: [{}, {}, {}],
            RIGHT_FOOT_INDEX: [{}, {}, {}],
            NOSE_INDEX: [{}, {}, {}],
            LEFT_SHOULDER_INDEX: [{}, {}, {}],
            RIGHT_SHOULDER_INDEX: [{}, {}, {}]
        }

        # FPS adaptation
        self.current_fps = 30.0
        self.required_stable_frames = self.config.required_stable_frames_per_30_fps
        
        # Initialize movement detectors
        self.movement_detectors: Dict[str, BaseMovement] = {
            "step": StepMovement(self),
            "jump": JumpMovement(self),
            "bend": BendMovement(self)
        }
        
        # Initialize sound manager only if sound is enabled
        self.sound_manager = None
        if self.config.sound_enabled:
            self.sound_manager = SoundManager(volume=self.config.sound_volume)
            if self.debug:
                self.logger.debug(f"Sound manager initialized with volume {self.config.sound_volume}")
        elif self.debug:
            self.logger.debug("Sound is disabled in config")
        
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
            self.logger.debug(f"FPS: {self.current_fps:.1f}, FPS ratio: {fps_ratio:.2f}, Required stable frames: {self.required_stable_frames}")

    def get_points_distance(self, point_num: int, type_point_index: int) -> Tuple[float, bool]:
        """Get the distance and direction of a point's movement"""
        return self.points_distance[point_num][type_point_index]["points"], self.points_distance[point_num][type_point_index]["is_position_smaller"]
    
    def update_landmarks_history(self, landmark_points: np.ndarray) -> None:
        """Maintain history of landmark points for movement detection"""
        if self.prev_landmarks is None:
            self.prev_landmarks = [landmark_points] * self.config.num_frames_to_check
        else:
            self.prev_landmarks.insert(0, landmark_points)
            self.prev_landmarks.pop()
    
    def map_points_distance(self) -> None:
        """Map the points distance to the points_distance dictionary"""
        for point_index, coordinates in self.points_distance.items():
            for i in range(3):
                current_point = self.prev_landmarks[0][point_index][i]
                prev_point = self.prev_landmarks[self.config.num_frames_to_check - 1][point_index][i]
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
        for detector in self.movement_detectors.values():
            detector.update_stability_and_motion_status()
        
        # Consider overall stability based on step movement (as in original code)
        if isinstance(self.movement_detectors["step"], StepMovement):
            step_detector = self.movement_detectors["step"]
            self.is_stable = step_detector.is_left_foot_stable_x or step_detector.is_right_foot_stable_x
            
            # Update overall stability counter
            if self.is_stable:
                self.stable_counter = self.required_stable_frames
            else:
                self.stable_counter = 0
                
        return self.is_stable

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

    def _after_movement_detected(self, movement: str) -> None:
        """Handle common tasks after any movement is detected
        
        Args:
            movement: The detected movement type
        """
        # Inform the appropriate movement detector that its movement was detected
        if movement.startswith("Step"):
            self.movement_detectors["step"].on_movement_detected()
        elif movement == "Jump":
            self.movement_detectors["jump"].on_movement_detected()
        elif movement == "Bend":
            self.movement_detectors["bend"].on_movement_detected()
        
        # Play the movement sound if enabled
        if self.sound_manager is not None:
            self.sound_manager.play_movement_sound(movement)
            
        self.last_detection_time = time.time()
        if self.debug:
            self.logger.debug(f"Movement detected: {movement}")

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
        self.map_points_distance()
        
        self.update_is_stable_general()  # This now updates all movement detectors
        
        # Debug logs for landmark positions if needed
        if self.debug:
            nose = landmarks.landmark[NOSE_INDEX]
            left_foot = landmarks.landmark[LEFT_FOOT_INDEX]
            right_foot = landmarks.landmark[RIGHT_FOOT_INDEX]
            left_hip = landmarks.landmark[LEFT_HIP_INDEX]
            right_hip = landmarks.landmark[RIGHT_HIP_INDEX]
            self.logger.debug(f"Left hip: x={left_hip.x:.4f}, y={left_hip.y:.4f}, z={left_hip.z:.4f}, visibility={left_hip.visibility:.2f}")
            self.logger.debug(f"Right hip: x={right_hip.x:.4f}, y={right_hip.y:.4f}, z={right_hip.z:.4f}, visibility={right_hip.visibility:.2f}")
            self.logger.debug(f"Nose position: x={nose.x:.4f}, y={nose.y:.4f}, z={nose.z:.4f}, visibility={nose.visibility:.2f}")
            self.logger.debug(f"Left foot: x={left_foot.x:.4f}, y={left_foot.y:.4f}, z={left_foot.z:.4f}, visibility={left_foot.visibility:.2f}")
            self.logger.debug(f"Right foot: x={right_foot.x:.4f}, y={right_foot.y:.4f}, z={right_foot.z:.4f}, visibility={right_foot.visibility:.2f}")

        # Check if any detector is already in motion
        if any(detector.is_in_motion for detector in self.movement_detectors.values()):
            self.logger.debug(f"MovementAnalyzer: Movement already in motion, skipping detection because of {[detector.name for detector in self.movement_detectors.values() if detector.is_in_motion]}")
            return None

        # Try to detect movements using specialized detectors
        # Order matters - jumped handled first as in original code
        jump_movement = self.movement_detectors["jump"].detect()
        if jump_movement:
            self._after_movement_detected(jump_movement)
            return jump_movement
            
        bend_movement = self.movement_detectors["bend"].detect()
        if bend_movement:
            self._after_movement_detected(bend_movement)
            return bend_movement
            
        step_movement = self.movement_detectors["step"].detect()
        if step_movement:
            self._after_movement_detected(step_movement)
            return step_movement
            
        return None