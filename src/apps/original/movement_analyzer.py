import numpy as np
import time
import logging
from typing import Optional, List, Tuple, Dict
import mediapipe as mp
from config import MovementConfig
from .movements.step_movement import StepMovement
from .movements.jump_movement import JumpMovement
from .movements.bend_movement import BendMovement
from .movements.base_movement import BaseMovement
from src.base_movement_analyzer import BaseMovementAnalyzer

from src.constants import (
    LEFT_FOOT_INDEX, RIGHT_FOOT_INDEX, NOSE_INDEX, 
    LEFT_KNEE_INDEX, RIGHT_KNEE_INDEX,
    LEFT_SHOULDER_INDEX, RIGHT_SHOULDER_INDEX,
    X_COORDINATE_INDEX, Y_COORDINATE_INDEX, Z_COORDINATE_INDEX,
    LEFT_HIP_INDEX, RIGHT_HIP_INDEX,
    LEFT_HEEL_INDEX, RIGHT_HEEL_INDEX,
    STEP_RIGHT, STEP_LEFT, JUMP, BEND
)

class MovementAnalyzer(BaseMovementAnalyzer):
    """Analyzes pose landmarks to detect specific movements"""
    
    def __init__(self, config: MovementConfig, mp_pose, debug: bool = False):
        super().__init__(config, mp_pose, debug)
        
        # Initialize movement detectors
        self.movement_detectors = [
            StepMovement(self, debug=True),
            JumpMovement(self, debug=False),
            BendMovement(self, debug=False)
        ]
            
    def _try_set_base_height(self, landmark_points: np.ndarray) -> None:
        """
        Attempts to set the base_height if the person is standing straight and still.
        This is called only if self.base_height is None.
        """
        if self.base_height is not None:
            return

        # Ensure enough frames have been processed for a meaningful stillness check
        # self.config.num_frames_to_check_per_30_fps should ideally be > 1
        if self.frame_counter < self.num_frames_to_check or self.num_frames_to_check <= 1:
            if self.debug:
                self.logger.debug(
                    f"Base height check: Not enough frames processed or num_frames_to_check_per_30_fps too small "
                    f"({self.frame_counter}/{self.config.num_frames_to_check_per_30_fps}) for stillness check."
                )
            return

        # Check vertical ordering (y is smaller for higher points)
        nose_y = landmark_points[NOSE_INDEX][Y_COORDINATE_INDEX]
        mid_shoulder_y = (landmark_points[LEFT_SHOULDER_INDEX][Y_COORDINATE_INDEX] + 
                          landmark_points[RIGHT_SHOULDER_INDEX][Y_COORDINATE_INDEX]) / 2
        mid_hip_y = (landmark_points[LEFT_HIP_INDEX][Y_COORDINATE_INDEX] + 
                     landmark_points[RIGHT_HIP_INDEX][Y_COORDINATE_INDEX]) / 2
        mid_knee_y = (landmark_points[LEFT_KNEE_INDEX][Y_COORDINATE_INDEX] + 
                      landmark_points[RIGHT_KNEE_INDEX][Y_COORDINATE_INDEX]) / 2
        mid_foot_y = (landmark_points[LEFT_FOOT_INDEX][Y_COORDINATE_INDEX] + 
                      landmark_points[RIGHT_FOOT_INDEX][Y_COORDINATE_INDEX]) / 2

        is_vertically_ordered = (nose_y < mid_shoulder_y < mid_hip_y < mid_knee_y < mid_foot_y)

        # Check horizontal alignment
        nose_x = landmark_points[NOSE_INDEX][X_COORDINATE_INDEX]
        mid_shoulder_x = (landmark_points[LEFT_SHOULDER_INDEX][X_COORDINATE_INDEX] + 
                          landmark_points[RIGHT_SHOULDER_INDEX][X_COORDINATE_INDEX]) / 2
        mid_hip_x = (landmark_points[LEFT_HIP_INDEX][X_COORDINATE_INDEX] + 
                     landmark_points[RIGHT_HIP_INDEX][X_COORDINATE_INDEX]) / 2
        mid_foot_x = (landmark_points[LEFT_FOOT_INDEX][X_COORDINATE_INDEX] + 
                      landmark_points[RIGHT_FOOT_INDEX][X_COORDINATE_INDEX]) / 2
        
        central_points_x = [nose_x, mid_shoulder_x, mid_hip_x, mid_foot_x]
        x_spread = max(central_points_x) - min(central_points_x)
        is_horizontally_aligned = x_spread < self.config.straight_pose_x_spread_threshold

        # Check for stillness (nose movement)
        # landmark_points is current, self.prev_landmarks[self.config.num_frames_to_check_per_30_fps - 1] is oldest
        nose_current_pos_xy = landmark_points[NOSE_INDEX][:2] 
        nose_prev_pos_xy = self.prev_landmarks[self.config.num_frames_to_check_per_30_fps - 1][NOSE_INDEX][:2]
        nose_movement = np.linalg.norm(nose_current_pos_xy - nose_prev_pos_xy)
        is_still = nose_movement < self.config.stillness_threshold

        if is_vertically_ordered and is_horizontally_aligned and is_still:
            calculated_height = mid_foot_y - nose_y  # Normalized height
            if calculated_height > self.config.min_base_height_threshold:
                self.base_height = calculated_height
                if self.debug:
                    self.logger.info(f"Base height SET to: {self.base_height:.4f} "
                                     f"(Vertical: {is_vertically_ordered}, X-Spread: {x_spread:.4f}, "
                                     f"Still (Nose Move): {nose_movement:.4f})")
            elif self.debug:
                self.logger.debug(f"Base height check: Calculated height {calculated_height:.4f} too small "
                                  f"(threshold: {self.config.min_base_height_threshold}). Conditions met: "
                                  f"Vertical: {is_vertically_ordered}, X-Spread: {x_spread:.4f}, Still: {is_still}.")
        elif self.debug:
            log_msg = "Base height check failed: "
            if not is_vertically_ordered:
                log_msg += (f"Vertical order incorrect (NoseY: {nose_y:.2f}, ShY: {mid_shoulder_y:.2f}, "
                            f"HipY: {mid_hip_y:.2f}, KnY: {mid_knee_y:.2f}, FtY: {mid_foot_y:.2f}). ")
            if not is_horizontally_aligned:
                log_msg += f"X-Spread too large: {x_spread:.4f} (limit: {self.config.straight_pose_x_spread_threshold}). "
            if not is_still:
                log_msg += f"Not still (Nose Move): {nose_movement:.4f} (limit: {self.config.stillness_threshold})."
            self.logger.debug(log_msg)
            
    def _log_debug_info(self, landmarks, landmark_points):
        """Override of base class method for custom debug logging"""
        if not self.debug:
            return
            
        # Basic landmark position logging
        nose = landmarks.landmark[NOSE_INDEX]
        left_foot = landmarks.landmark[LEFT_FOOT_INDEX]
        right_foot = landmarks.landmark[RIGHT_FOOT_INDEX]

        self.logger.debug(f"Nose position: x={nose.x:.4f}, y={nose.y:.4f}, z={nose.z:.4f}, visibility={nose.visibility:.2f}")
        self.logger.debug(f"Left foot: x={left_foot.x:.4f}, y={left_foot.y:.4f}, z={left_foot.z:.4f}, visibility={left_foot.visibility:.2f}")
        self.logger.debug(f"Right foot: x={right_foot.x:.4f}, y={right_foot.y:.4f}, z={right_foot.z:.4f}, visibility={right_foot.visibility:.2f}")
        
        # Add debug logs for left and right foot distance and direction
        left_foot_y_dist, left_foot_y_dir = self.get_points_distance(LEFT_FOOT_INDEX, Y_COORDINATE_INDEX)
        right_foot_y_dist, right_foot_y_dir = self.get_points_distance(RIGHT_FOOT_INDEX, Y_COORDINATE_INDEX)
        left_foot_z_dist, left_foot_z_dir = self.get_points_distance(LEFT_FOOT_INDEX, Z_COORDINATE_INDEX)
        right_foot_z_dist, right_foot_z_dir = self.get_points_distance(RIGHT_FOOT_INDEX, Z_COORDINATE_INDEX)
        
        self.logger.debug(f"Left foot Z: distance={left_foot_z_dist:.4f}, direction={'decreasing' if left_foot_z_dir else 'increasing'}")
        self.logger.debug(f"Right foot Z: distance={right_foot_z_dist:.4f}, direction={'decreasing' if right_foot_z_dir else 'increasing'}")
        
        left_shoulder_knee_dist = np.linalg.norm(landmark_points[LEFT_SHOULDER_INDEX] - landmark_points[LEFT_KNEE_INDEX])
        right_shoulder_knee_dist = np.linalg.norm(landmark_points[RIGHT_SHOULDER_INDEX] - landmark_points[RIGHT_KNEE_INDEX])

        if self.base_height and self.base_height > 1e-6:  # Check if base_height is set and not zero/too small
            left_percentage = (left_shoulder_knee_dist / self.base_height) * 100
            right_percentage = (right_shoulder_knee_dist / self.base_height) * 100
            

    def map_core_data(self, landmark_points):
        self._try_set_base_height(landmark_points)
        super().map_core_data(landmark_points)

