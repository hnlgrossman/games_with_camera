import numpy as np
import time
import logging
from typing import Optional, List, Tuple, Dict
import mediapipe as mp
from config import MovementConfig

from .movements.aside_movement import AsideMovement
# from .movements.linear_movement import LinearMovement

from src.base_movement_analyzer import BaseMovementAnalyzer

from src.constants import (
    X_COORDINATE_INDEX, Y_COORDINATE_INDEX,
    LEFT_WRIST_INDEX, RIGHT_WRIST_INDEX
)

class MovementAnalyzer(BaseMovementAnalyzer):
    """Analyzes pose landmarks to detect specific movements"""
    
    def __init__(self, config: MovementConfig, mp_pose, debug: bool = False):
        super().__init__(config, mp_pose, debug)
        
        # Initialize movement detectors
        self.movement_detectors = [
            AsideMovement(self, debug),
            # LinearMovement(self, debug)
        ]

        self.required_landmarks = [
            LEFT_WRIST_INDEX,
            RIGHT_WRIST_INDEX
        ]

    def _log_debug_info(self):
        """Override of base class method for custom debug logging"""
        if not self.debug:
            return
        
        if self.current_landmark_points is not None:
            # Log hand locations
            left_hand_x = self.current_landmark_points[LEFT_WRIST_INDEX][X_COORDINATE_INDEX]
            left_hand_y = self.current_landmark_points[LEFT_WRIST_INDEX][Y_COORDINATE_INDEX]
            right_hand_x = self.current_landmark_points[RIGHT_WRIST_INDEX][X_COORDINATE_INDEX]
            right_hand_y = self.current_landmark_points[RIGHT_WRIST_INDEX][Y_COORDINATE_INDEX]
            
            self.logger.debug(f"MovementAnalyzer: hand locations - hand: ({left_hand_y:.3f}, {right_hand_y:.3f})")

    def update_is_stable_general(self) -> bool:
        pass
    
    def update_before_detect(self, landmark_points):
        super().update_before_detect(landmark_points)

    
            
