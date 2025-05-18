import numpy as np
import time
import logging
from typing import Optional, List, Tuple, Dict
import mediapipe as mp
from config import MovementConfig
from .movements.linear_movement import LinearMovement
from .movements.aside_movement import AsideMovement
# from .movements.base_movement import BaseMovement

from src.base_movement_analyzer import BaseMovementAnalyzer

from src.constants import (
    LEFT_FOOT_INDEX, RIGHT_FOOT_INDEX, Z_COORDINATE_INDEX
)

class MovementAnalyzer(BaseMovementAnalyzer):
    """Analyzes pose landmarks to detect specific movements"""
    
    def __init__(self, config: MovementConfig, mp_pose, debug: bool = False):
        super().__init__(config, mp_pose, debug)
        
        # Initialize movement detectors
        self.movement_detectors = [
            LinearMovement(self, debug=True),
            AsideMovement(self, debug=False),
        ]

        self.is_general_stable = True
        self.is_general_stable_counter = 0

        self.is_left_foot_forward = True

        self.required_stable_frames_per_30_fps = 4
        self.required_stable_frames = 4

        self.stable_foot_z_threshold = 0.02

        self.stable_counter_left_foot = 0
        self.stable_counter_right_foot = 0

        self.foots_distance_linear_threshold = 0.1

    def _log_debug_info(self, landmarks, landmark_points):
        """Override of base class method for custom debug logging"""
        if not self.debug:
            return
        
    def _update_single_joint_stability(self, joint_index: int, is_left: bool) -> bool:
        """Updates stability for a single foot joint based on Z-coordinate and returns its stability status."""
        # Only process foot joints
        if joint_index != LEFT_FOOT_INDEX and joint_index != RIGHT_FOOT_INDEX:
            return False
            
        side = "left" if is_left else "right"
        foot_distance_z, _ = self.get_points_distance(joint_index, Z_COORDINATE_INDEX)
        
        counter_name = f"{side}_foot"
        current_counter = getattr(self, f"stable_counter_{counter_name}", 0)
        
        required_frames = self.required_stable_frames

        # Check Z stability
        if foot_distance_z < self.stable_foot_z_threshold:
            current_counter += 1
            if self.debug:
                self.logger.debug(f"MovementAnalyzer: {side.title()} foot Z stability counter: {current_counter}/{required_frames} diff: {foot_distance_z:.4f}")
            is_stable = current_counter >= required_frames
        else:
            if self.debug and current_counter > 0:
                self.logger.debug(f"MovementAnalyzer: Reset {side} foot Z stability counter")
            current_counter = 0
            is_stable = False

        if self.debug:
            self.logger.debug(f"MovementAnalyzer: {side} foot Z diff {foot_distance_z:.4f}")
            
        setattr(self, f"stable_counter_{counter_name}", current_counter)
        setattr(self, f"is_{counter_name}_stable", is_stable)

        return is_stable
            
    def _update_z_foot_distance(self):
        right_foot_z = self.current_landmark_points[RIGHT_FOOT_INDEX][Z_COORDINATE_INDEX]
        left_foot_z = self.current_landmark_points[LEFT_FOOT_INDEX][Z_COORDINATE_INDEX]

        self.foots_distance = round(abs(right_foot_z - left_foot_z), 3)
        self.is_left_foot_forward = right_foot_z > left_foot_z

        if self.debug:
            self.logger.debug(f"MovementAnalyzer: foots_distance={self.foots_distance}, is_left_foot_forward={self.is_left_foot_forward}")


    def update_is_stable_general(self) -> bool:
        print(f"Checking stability for left and right foot")
        is_left_foot_stable = self._update_single_joint_stability(LEFT_FOOT_INDEX, is_left=True)
        is_right_foot_stable = self._update_single_joint_stability(RIGHT_FOOT_INDEX, is_left=False)
        print(f"Stability status: left foot={is_left_foot_stable}, right foot={is_right_foot_stable}")

        self.is_general_stable = is_left_foot_stable and is_right_foot_stable
        if self.is_general_stable:
            for detector in self.movement_detectors:
                if detector.is_in_motion:
                    detector.is_in_motion = False
                    if self.debug:
                        self.logger.debug(f"MovementAnalyzer: Resetting is_in_motion because movement is stable for {detector.name}.")


        # if self.foots_distance < self.stable_foot_z_threshold:
        #     self.is_general_stable_counter += 1
        #     print(f"Feet are stable: distance={self.foots_distance}, counter={self.is_general_stable_counter}")
        #     if self.is_general_stable_counter >= self.required_stable_frames:
        #         self.is_general_stable = True

        #         for detector in self.movement_detectors:
        #             if detector.is_in_motion:
        #                 detector.is_in_motion = False
        #                 if self.debug:
        #                     self.logger.debug(f"MovementAnalyzer: Resetting is_in_motion because movement is stable for {detector.name}.")

        #         print(f"General stability achieved after {self.is_general_stable_counter} frames")
        # else:
        #     print(f"Stability lost: distance={self.foots_distance} exceeds threshold {self.stable_foot_z_threshold}")
        #     if self.is_general_stable_counter > 0:
        #         self.is_general_stable_counter = 0
        #         self.is_general_stable = False
    
    def update_before_detect(self, landmark_points):
        self.required_stable_frames = self.get_per_30_fps(self.required_stable_frames_per_30_fps)
        self._update_z_foot_distance()
        super().update_before_detect(landmark_points)


    
            
