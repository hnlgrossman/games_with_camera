from typing import Optional, TYPE_CHECKING, List, Tuple
from .base_movement import BaseMovement
from src.constants import (
    LEFT_FOOT_INDEX, RIGHT_FOOT_INDEX, Y_COORDINATE_INDEX, X_COORDINATE_INDEX, 
    NOSE_INDEX, JUMP, LEFT_HIP_INDEX, RIGHT_HIP_INDEX
)

if TYPE_CHECKING:
    from src.movement_analyzer import MovementAnalyzer # To avoid circular import

class JumpMovement(BaseMovement):
    """Detects jump movements."""

    def __init__(self, analyzer: 'MovementAnalyzer'):
        super().__init__(analyzer)

        # Stability counters and flags
        self.stable_counter_left_foot: int = 0
        self.stable_counter_right_foot: int = 0
        self.is_left_foot_stable_y: bool = True
        self.is_right_foot_stable_y: bool = True

        self.require_foots_stable_frames = 2

        # Motion state
        self.is_stable_for_detection: bool = True # Analogous to old is_stable_move["jump"]

        self.hip_x_distance_to_outrange = 0.01

        self.foot_y_stable_distance = 0.005
        
        self.nose_y_distance = 0.06;
        self.motion_counter_nose: int = 0
        self.require_nose_motion_frames: int = 2
    

    @property
    def detectable_moves(self) -> List[str]:
        """Returns the list of movement types this detector can detect."""
        return [JUMP]

    def _update_single_foot_stability(self, is_left_foot: bool) -> bool:
        """Updates stability for a single foot and returns its stability status."""
        foot_index = LEFT_FOOT_INDEX if is_left_foot else RIGHT_FOOT_INDEX
        foot_distance, _ = self.analyzer.get_points_distance(foot_index, Y_COORDINATE_INDEX)
        
        counter_name = "left foot" if is_left_foot else "right foot"
        current_counter = self.stable_counter_left_foot if is_left_foot else self.stable_counter_right_foot
        
        required_frames = self.require_foots_stable_frames

        # Using jump stability threshold from config
        if foot_distance < self.foot_y_stable_distance:
            current_counter += 1
            if self.debug:
                self.logger.debug(f"JumpMovement: {counter_name.title()} stability counter: {current_counter}/{required_frames} diff: {foot_distance}")
            is_stable = current_counter >= required_frames
        else:
            if self.debug and current_counter > 0:
                self.logger.debug(f"JumpMovement: Reset {counter_name} stability counter. Distance: {foot_distance:.4f}")
            current_counter = 0
            is_stable = False
            
        if is_left_foot:
            self.stable_counter_left_foot = current_counter
            self.is_left_foot_stable_y = is_stable
        else:
            self.stable_counter_right_foot = current_counter
            self.is_right_foot_stable_y = is_stable
        return is_stable
    
    def _update_nose_motion_counter(self):
        current_counter = self.motion_counter_nose;
        required_frames = self.require_nose_motion_frames;
        nose_distance, is_foot_dir_up = self.analyzer.get_points_distance(NOSE_INDEX, Y_COORDINATE_INDEX)

        # Using jump stability threshold from config
        if is_foot_dir_up and nose_distance > self.nose_y_distance:
            current_counter += 1
            if self.debug:
                self.logger.debug(f"JumpMovement: NOSE_INDEX motion counter: {current_counter}/{required_frames} distance: {nose_distance}")
        else:
            if self.debug and current_counter > 0:
                self.logger.debug(f"JumpMovement: Reset NOSE_INDEX motion counter. Distance: {nose_distance:.4f} dir: {is_foot_dir_up}")
            current_counter = 0
            

        self.motion_counter_nose = current_counter        

    def update_stability_and_motion_status(self) -> None:
        """Updates feet stability on Y axis and determines if a new jump detection can occur."""
        self._update_single_foot_stability(is_left_foot=True)
        self._update_single_foot_stability(is_left_foot=False)

        self._update_nose_motion_counter()
        # Jump is stable for detection only when both feet are stable
        self.is_stable_for_detection = self.is_left_foot_stable_y and self.is_right_foot_stable_y
        
        if self.debug:
            self.logger.debug(f"JumpMovement: Stability for detection (both feet stable): {self.is_stable_for_detection}")

        if self.is_stable_for_detection:
            if self.is_in_motion:
                if self.debug:
                    self.logger.debug("JumpMovement: Resetting is_in_motion because movement is stable.")
                self.is_in_motion = False

    def detect(self) -> Optional[str]:
        """Detects a jump based on both feet moving upward."""
        if self.is_in_motion or self.motion_counter_nose < self.require_nose_motion_frames: # If already jumping, don't detect another jump
            return None
        
        # Get distance and direction for both hips
        left_hip_distance_x, left_hip_dir_left = self.analyzer.get_points_distance(LEFT_HIP_INDEX, X_COORDINATE_INDEX)
        right_hip_distance_x, right_hip_dir_left = self.analyzer.get_points_distance(RIGHT_HIP_INDEX, X_COORDINATE_INDEX)
        if (left_hip_dir_left and left_hip_distance_x > self.hip_x_distance_to_outrange):
            if self.debug:
                self.logger.debug("JumpMovement: Left hip out of range")
            return None
        if(not right_hip_dir_left and right_hip_distance_x > self.hip_x_distance_to_outrange):
            if self.debug:
                self.logger.debug(f"JumpMovement: Right hip out of range: {right_hip_distance_x}")
            return None

        left_foot_distance, left_foot_dir_up = self.analyzer.get_points_distance(LEFT_FOOT_INDEX, Y_COORDINATE_INDEX)
        right_foot_distance, right_foot_dir_up = self.analyzer.get_points_distance(RIGHT_FOOT_INDEX, Y_COORDINATE_INDEX)
        if self.debug:
            self.logger.debug(f"JumpMovement: Left foot diff: {left_foot_distance:.4f}, Right foot diff: {right_foot_distance:.4f} dir_down: {left_foot_dir_up}, {right_foot_dir_up}")

        # Jump is detected when:
        # 1. Not stable for detection (feet are moving)
        # 2. Both feet are moving upward (not dir_down)
        # 3. Both feet distances exceed jump threshold
        if (not self.is_stable_for_detection and 
            left_foot_dir_up and right_foot_dir_up and
            left_foot_distance > self.config.jump_threshold and
            right_foot_distance > self.config.jump_threshold):
            
            if self.debug:
                self.logger.debug(f"JumpMovement: Jump detected - Left foot diff: {left_foot_distance:.4f}, Right foot diff: {right_foot_distance:.4f}")
            return JUMP
            
        return None 