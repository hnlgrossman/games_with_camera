from typing import Optional, TYPE_CHECKING, List
from .base_movement import BaseMovement
from src.constants import (
    Y_COORDINATE_INDEX, X_COORDINATE_INDEX,
    LEFT_SHOULDER_INDEX, RIGHT_SHOULDER_INDEX,
    LEFT_FOOT_INDEX, RIGHT_FOOT_INDEX,
    BEND, NOSE_INDEX
)

if TYPE_CHECKING:
    from src.apps.original.movement_analyzer import MovementAnalyzer # To avoid circular import

class BendMovement(BaseMovement):
    """Detects bend movements."""

    def __init__(self, analyzer: 'MovementAnalyzer', debug: bool = False):
        super().__init__(analyzer, debug)

        # Stability counters and flags for shoulders
        self.stable_counter_left_shoulder: int = 0
        self.stable_counter_right_shoulder: int = 0
        self.is_left_shoulder_stable_y: bool = True
        self.is_right_shoulder_stable_y: bool = True

        # Stability counters and flags for feet
        self.stable_counter_left_foot_x: int = 0
        self.stable_counter_right_foot_x: int = 0
        self.is_left_foot_stable_x: bool = True
        self.is_right_foot_stable_x: bool = True
        self.stable_counter_left_foot_y: int = 0
        self.stable_counter_right_foot_y: int = 0
        self.is_left_foot_stable_y: bool = True
        self.is_right_foot_stable_y: bool = True

        self.is_ready_for_next_move = True

        self.foot_x_distance_to_outrange = 0.01

        self.get_required_stable_frames = 4


        self.nose_y_distance = 0.01
        
        # Motion state
        self.is_stable_for_detection: bool = True # Now includes foot stability

    @property
    def detectable_moves(self) -> List[str]:
        """Returns the list of movement types this detector can detect."""
        return [BEND]

    def _update_single_shoulder_stability(self, is_left_shoulder: bool) -> bool:
        """Updates stability for a single shoulder and returns its stability status."""
        shoulder_index = LEFT_SHOULDER_INDEX if is_left_shoulder else RIGHT_SHOULDER_INDEX
        shoulder_distance, _ = self.analyzer.get_points_distance(shoulder_index, Y_COORDINATE_INDEX)
        
        counter_name = "left shoulder" if is_left_shoulder else "right shoulder"
        current_counter = self.stable_counter_left_shoulder if is_left_shoulder else self.stable_counter_right_shoulder
        
        required_frames = self.get_required_stable_frames

        # Using bend stability threshold from config
        if shoulder_distance < self.config.stability_moves_threshold.get("bend", 0.01):
            current_counter += 1
            if self.debug:
                self.logger.debug(f"BendMovement: {counter_name.title()} stability counter: {current_counter}/{required_frames}")
            is_stable = current_counter >= required_frames
        else:
            if self.debug and current_counter > 0:
                self.logger.debug(f"BendMovement: Reset {counter_name} stability counter. Distance: {shoulder_distance:.4f}")
            current_counter = 0
            is_stable = False
            
        if is_left_shoulder:
            self.stable_counter_left_shoulder = current_counter
            self.is_left_shoulder_stable_y = is_stable
        else:
            self.stable_counter_right_shoulder = current_counter
            self.is_right_shoulder_stable_y = is_stable
        return is_stable

    def _update_single_foot_stability(self, is_left_foot: bool, axis_index: int) -> bool:
        """Updates stability for a single foot on a given axis and returns its stability status."""
        foot_index = LEFT_FOOT_INDEX if is_left_foot else RIGHT_FOOT_INDEX
        foot_distance, _ = self.analyzer.get_points_distance(foot_index, axis_index)
        
        foot_side = "left" if is_left_foot else "right"
        axis_name = "X" if axis_index == X_COORDINATE_INDEX else "Y"
        
        if axis_index == X_COORDINATE_INDEX:
            current_counter = self.stable_counter_left_foot_x if is_left_foot else self.stable_counter_right_foot_x
        else: # Y_COORDINATE_INDEX
            current_counter = self.stable_counter_left_foot_y if is_left_foot else self.stable_counter_right_foot_y
            
        required_frames = self.get_required_stable_frames

        # Using a general stability threshold, consider if a specific one for feet is needed
        # For now, using the "bend" stability threshold as a placeholder, this might need adjustment
        stability_threshold = self.foot_x_distance_to_outrange

        if foot_distance < stability_threshold:
            current_counter += 1
            if self.debug:
                self.logger.debug(f"BendMovement: {foot_side.title()} foot {axis_name}-axis stability counter: {current_counter}/{required_frames}")
            is_stable = current_counter >= required_frames
        else:
            if self.debug and current_counter > 0:
                self.logger.debug(f"BendMovement: Reset {foot_side} foot {axis_name}-axis stability counter. Distance: {foot_distance:.4f}")
            current_counter = 0
            is_stable = False
            
        if is_left_foot:
            if axis_index == X_COORDINATE_INDEX:
                self.stable_counter_left_foot_x = current_counter
                self.is_left_foot_stable_x = is_stable
            else:
                self.stable_counter_left_foot_y = current_counter
                self.is_left_foot_stable_y = is_stable
        else: # Right foot
            if axis_index == X_COORDINATE_INDEX:
                self.stable_counter_right_foot_x = current_counter
                self.is_right_foot_stable_x = is_stable
            else:
                self.stable_counter_right_foot_y = current_counter
                self.is_right_foot_stable_y = is_stable
        return is_stable

    def _update_ready_for_next_move(self):
        # if self.is_ready_for_next_move:
        #     return
        
        nose_distance, is_foot_dir_up = self.analyzer.get_points_distance(NOSE_INDEX, Y_COORDINATE_INDEX)

        # Using jump stability threshold from config
        if is_foot_dir_up and nose_distance > self.nose_y_distance:
            self.is_ready_for_next_move = True
            # if self.debug:
            #     self.logger.debug(f"JumpMovement: NOSE_INDEX motion counter: {current_counter}/{required_frames} distance: {nose_distance}")
        else:
            self.is_ready_for_next_move = False
          

    def update_stability_and_motion_status(self) -> None:
        """Updates shoulders stability on Y axis and determines if a new bend detection can occur."""
        # Update shoulder stability (original logic commented out, assuming it might be re-integrated or handled elsewhere)
        # self._update_single_shoulder_stability(is_left_shoulder=True)
        # self._update_single_shoulder_stability(is_left_shoulder=False)

        # Update foot stability
        self._update_single_foot_stability(is_left_foot=True, axis_index=X_COORDINATE_INDEX)
        self._update_single_foot_stability(is_left_foot=False, axis_index=X_COORDINATE_INDEX)
        self._update_single_foot_stability(is_left_foot=True, axis_index=Y_COORDINATE_INDEX)
        self._update_single_foot_stability(is_left_foot=False, axis_index=Y_COORDINATE_INDEX)

        self._update_ready_for_next_move() # This seems to be about resetting after a move

        # Bend is stable for detection only when both feet are stable on both axes
        self.is_stable_for_detection = (
            self.is_left_foot_stable_x and self.is_right_foot_stable_x and
            self.is_left_foot_stable_y and self.is_right_foot_stable_y
        )
        
        if self.debug:
            self.logger.debug(f"BendMovement: is_stable_for_detection (feet stable X&Y): {self.is_stable_for_detection}")
            self.logger.debug(f"BendMovement: is_ready_for_next_move (nose logic): {self.is_ready_for_next_move}")

        # This part seems to be about resetting is_in_motion if the *overall conditions* are met
        # The condition self.is_ready_for_next_move might need to be re-evaluated in context of foot stability
        # For now, keeping original logic.
        if self.is_ready_for_next_move: # and self.is_stable_for_detection: # Consider adding foot stability here too for resetting motion
            if self.is_in_motion:
                if self.debug:
                    self.logger.debug("BendMovement: Resetting is_in_motion because movement is stable (based on nose and/or feet).")
                self.is_in_motion = False
    
    def detect(self) -> Optional[str]:
        """Detects a bend based on both shoulders moving downward, only if feet are stable."""
        if not self.is_stable_for_detection: # Check for foot stability first
            if self.debug:
                self.logger.debug("BendMovement: Feet are not stable. Skipping bend detection.")
            return None
            
        if self.is_in_motion: # If already bending, don't detect another bend
            return None

        # Get distance and direction for both shoulders
        left_shoulder_distance, is_left_shoulder_moving_up = self.analyzer.get_points_distance(LEFT_SHOULDER_INDEX, Y_COORDINATE_INDEX)
        right_shoulder_distance, is_right_shoulder_moving_up = self.analyzer.get_points_distance(RIGHT_SHOULDER_INDEX, Y_COORDINATE_INDEX)

        if self.debug:
            self.logger.debug(f"BendMovement: Left shoulder diff: {left_shoulder_distance:.4f}, Right shoulder diff: {right_shoulder_distance:.4f}, is_left_shoulder_moving_up: {is_left_shoulder_moving_up}, is_right_shoulder_moving_up: {is_right_shoulder_moving_up}")

        # Bend is detected when:
        # 1. Not stable for detection (shoulders are moving)
        # 2. Both shoulders distances exceed bend threshold
        is_bend_detected = not is_left_shoulder_moving_up and not is_right_shoulder_moving_up and left_shoulder_distance > self.config.bend_threshold and right_shoulder_distance > self.config.bend_threshold
        
        if self.debug:
            self.logger.debug(f"BendMovement: shuld Bend detected: {is_bend_detected}")
        if (is_bend_detected):
            
            if self.debug:
                self.logger.debug(f"BendMovement: Bend detected - Left shoulder diff: {left_shoulder_distance:.4f}, Right shoulder diff: {right_shoulder_distance:.4f}")
            return BEND
            
        return None