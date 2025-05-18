import numpy as np
import time
import logging
from typing import Optional, List, Tuple, Dict
import mediapipe as mp
from config import MovementConfig
from .movements.press_movement import PressMovement
# from .movements.base_movement import BaseMovement

from src.base_movement_analyzer import BaseMovementAnalyzer

from src.constants import (
    LEFT_FOOT_INDEX, RIGHT_FOOT_INDEX, Z_COORDINATE_INDEX, X_COORDINATE_INDEX, Y_COORDINATE_INDEX
)

class MovementAnalyzer(BaseMovementAnalyzer):
    """Analyzes pose landmarks to detect specific movements"""
    
    def __init__(self, config: MovementConfig, mp_pose, debug: bool = False):
        super().__init__(config, mp_pose, debug)
        
        # Initialize movement detectors
        self.movement_detectors = [
            PressMovement(self, debug=True),
        ]

        self.is_feet_stable = False;
        self.required_feet_stable_frames = 150
        self.feet_stable_counter = 0

        # Threshold for feet proximity
        self.feet_proximity_threshold = 0.05
        # Threshold for feet movement
        self.feet_movement_threshold = 0.01

        self.required_stable_frames_per_30_fps = 4
        self.required_stable_frames = 4

    def _log_debug_info(self, landmarks, landmark_points):
        """Override of base class method for custom debug logging"""
        if not self.debug:
            return

    def _update_feet_stability(self):
        """
        Updates is_feet_stable based on feet proximity and movement.
        Sets is_feet_stable to true when both feet are close to each other
        and not moving for self.required_feet_stable_frames frames.
        """
        # Calculate distance between feet in all dimensions
        left_foot = self.current_landmark_points[LEFT_FOOT_INDEX]
        right_foot = self.current_landmark_points[RIGHT_FOOT_INDEX]
        
        # Calculate Euclidean distance between feet
        feet_distance = np.linalg.norm(left_foot - right_foot)
        
        # Check movement of each foot using the points_distance dictionary
        left_foot_movement_x, _ = self.get_points_distance(LEFT_FOOT_INDEX, X_COORDINATE_INDEX)
        left_foot_movement_y, _ = self.get_points_distance(LEFT_FOOT_INDEX, Y_COORDINATE_INDEX)
        left_foot_movement_z, _ = self.get_points_distance(LEFT_FOOT_INDEX, Z_COORDINATE_INDEX)
        
        right_foot_movement_x, _ = self.get_points_distance(RIGHT_FOOT_INDEX, X_COORDINATE_INDEX)
        right_foot_movement_y, _ = self.get_points_distance(RIGHT_FOOT_INDEX, Y_COORDINATE_INDEX)
        right_foot_movement_z, _ = self.get_points_distance(RIGHT_FOOT_INDEX, Z_COORDINATE_INDEX)
        
        # Calculate total movement for each foot
        left_foot_movement = left_foot_movement_x + left_foot_movement_y + left_foot_movement_z
        right_foot_movement = right_foot_movement_x + right_foot_movement_y + right_foot_movement_z
        
        # Check if feet are close and not moving
        if (feet_distance < self.feet_proximity_threshold and 
            left_foot_movement < self.feet_movement_threshold and 
            right_foot_movement < self.feet_movement_threshold):
            
            self.feet_stable_counter += 1
            
            if self.debug:
                self.logger.debug(f"MovementAnalyzer: Feet stability counter: {self.feet_stable_counter}/{self.required_feet_stable_frames}")
                self.logger.debug(f"MovementAnalyzer: Feet distance: {feet_distance:.4f}, Left movement: {left_foot_movement:.4f}, Right movement: {right_foot_movement:.4f}")
            
            # Check if stable for required frames
            if self.feet_stable_counter >= self.required_feet_stable_frames:
                self.is_feet_stable = True
                if self.debug:
                    self.logger.debug("MovementAnalyzer: Feet are now stable")
        else:
            # Reset counter if feet are moving or not close
            if self.feet_stable_counter > 0:
                if self.debug:
                    self.logger.debug(f"MovementAnalyzer: Reset feet stability counter. Distance: {feet_distance:.4f}, Left movement: {left_foot_movement:.4f}, Right movement: {right_foot_movement:.4f}")
                self.feet_stable_counter = 0
                
            if self.is_feet_stable:
                self.is_feet_stable = False
                if self.debug:
                    self.logger.debug("MovementAnalyzer: Feet are no longer stable")

    def update_is_stable_general(self) -> bool:
        pass
    
    def update_before_detect(self, landmark_points):
        self.required_feet_stable_frames = self.get_per_30_fps(4)
        self._update_feet_stability()
        super().update_before_detect(landmark_points)


    
            
