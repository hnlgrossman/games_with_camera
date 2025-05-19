import numpy as np
import time
import logging
from typing import Optional, List, Tuple, Dict
import mediapipe as mp
from config import MovementConfig

from .movements.aside_movement import AsideMovement
from .movements.linear_movement import LinearMovement

from src.base_movement_analyzer import BaseMovementAnalyzer

from src.constants import (
    X_COORDINATE_INDEX, Y_COORDINATE_INDEX
)

class MovementAnalyzer(BaseMovementAnalyzer):
    """Analyzes pose landmarks to detect specific movements"""
    
    def __init__(self, config: MovementConfig, mp_pose, debug: bool = False):
        super().__init__(config, mp_pose, debug)
        
        # Initialize movement detectors
        self.movement_detectors = [
            AsideMovement(self, debug),
            LinearMovement(self, debug)
        ]

    def _log_debug_info(self):
        """Override of base class method for custom debug logging"""
        if not self.debug:
            return

    def update_is_stable_general(self) -> bool:
        pass
    
    def update_before_detect(self, landmark_points):
        super().update_before_detect(landmark_points)

    
            
