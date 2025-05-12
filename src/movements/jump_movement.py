from typing import Optional, TYPE_CHECKING, List, Tuple
from .base_movement import BaseMovement
from src.constants import (
    LEFT_FOOT_INDEX, RIGHT_FOOT_INDEX, Y_COORDINATE_INDEX, X_COORDINATE_INDEX, 
    NOSE_INDEX, JUMP, LEFT_HIP_INDEX, RIGHT_HIP_INDEX, LEFT_HEEL_INDEX, RIGHT_HEEL_INDEX
)

if TYPE_CHECKING:
    from src.movement_analyzer import MovementAnalyzer # To avoid circular import

class JumpMovement(BaseMovement):
    """Detects jump movements."""

    def __init__(self, analyzer: 'MovementAnalyzer', debug: bool = False):
        super().__init__(analyzer, debug)

        # Stability counters and flags for Foot Y-axis
        self.stable_counter_left_foot: int = 0
        self.stable_counter_right_foot: int = 0
        self.is_left_foot_stable_y: bool = True
        self.is_right_foot_stable_y: bool = True
        
        # Stability counters and flags for Foot X-axis
        self.stable_counter_left_foot_x: int = 0
        self.stable_counter_right_foot_x: int = 0
        self.is_left_foot_stable_x: bool = True
        self.is_right_foot_stable_x: bool = True

        # Stability counters and flags for Heel Y-axis
        self.stable_counter_left_heel: int = 0
        self.stable_counter_right_heel: int = 0
        self.is_left_heel_stable_y: bool = True
        self.is_right_heel_stable_y: bool = True

        # Stability counters and flags for Heel X-axis
        self.stable_counter_left_heel_x: int = 0
        self.stable_counter_right_heel_x: int = 0
        self.is_left_heel_stable_x: bool = True
        self.is_right_heel_stable_x: bool = True

        self.require_stable_frames = 3

        # Motion state
        self.is_stable_for_detection_foot: bool = True
        self.is_stable_for_detection_heel: bool = True 

        self.hip_x_distance_to_outrange = 0.01

        self.foot_y_stable_distance = 0.01
        self.foot_x_stable_distance = 0.01
        self.heel_y_stable_distance = 0.01
        self.heel_x_stable_distance = 0.01
        
        self.nose_y_distance = 0.04;
        self.motion_counter_nose: int = 0
        self.require_nose_motion_frames: int = 2
    

    @property
    def detectable_moves(self) -> List[str]:
        """Returns the list of movement types this detector can detect."""
        return [JUMP]

    def _update_single_joint_stability(self, joint_index: int, is_left: bool) -> bool:
        """Updates stability for a single joint (foot or heel) and returns its stability status."""
        is_foot = joint_index == LEFT_FOOT_INDEX or joint_index == RIGHT_FOOT_INDEX
        joint_name = "foot" if is_foot else "heel"
        side = "left" if is_left else "right"

        joint_distance_y, _ = self.analyzer.get_points_distance(joint_index, Y_COORDINATE_INDEX)
        joint_distance_x, _ = self.analyzer.get_points_distance(joint_index, X_COORDINATE_INDEX)
        
        counter_name_prefix = f"{side}_{joint_name}"
        current_counter_y = getattr(self, f"stable_counter_{counter_name_prefix}")
        current_counter_x = getattr(self, f"stable_counter_{counter_name_prefix}_x")
        
        y_stable_distance = self.foot_y_stable_distance if is_foot else self.heel_y_stable_distance
        x_stable_distance = self.foot_x_stable_distance if is_foot else self.heel_x_stable_distance

        required_frames = self.require_stable_frames

        # Check Y stability
        if joint_distance_y < y_stable_distance:
            current_counter_y += 1
            if self.debug:
                self.logger.debug(f"JumpMovement: {side.title()} {joint_name.title()} Y stability counter: {current_counter_y}/{required_frames} diff: {joint_distance_y:.4f}")
            is_stable_y = current_counter_y >= required_frames
        else:
            if self.debug and current_counter_y > 0:
                self.logger.debug(f"JumpMovement: Reset {side} {joint_name} Y stability counter")
            current_counter_y = 0
            is_stable_y = False

        # Check X stability
        if joint_distance_x < x_stable_distance:
            current_counter_x += 1
            if self.debug:
                self.logger.debug(f"JumpMovement: {side.title()} {joint_name.title()} X stability counter: {current_counter_x}/{required_frames} diff: {joint_distance_x:.4f}")
            is_stable_x = current_counter_x >= required_frames
        else:
            if self.debug and current_counter_x > 0:
                self.logger.debug(f"JumpMovement: Reset {side} {joint_name} X stability counter")
            current_counter_x = 0
            is_stable_x = False

        if self.debug:
            self.logger.debug(f"JumpMovement: TEMP {side} {joint_name} Y diff {joint_distance_y:.4f}, X diff {joint_distance_x:.4f}")
            
        setattr(self, f"stable_counter_{counter_name_prefix}", current_counter_y)
        setattr(self, f"is_{counter_name_prefix}_stable_y", is_stable_y)
        setattr(self, f"stable_counter_{counter_name_prefix}_x", current_counter_x)
        setattr(self, f"is_{counter_name_prefix}_stable_x", is_stable_x)

        # Overall joint stability requires both X and Y to be stable
        is_stable = is_stable_y and is_stable_x
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
        """Updates feet and heel stability and determines if a new jump detection can occur."""
        # Update foot stability
        left_foot_stable = self._update_single_joint_stability(LEFT_FOOT_INDEX, is_left=True)
        right_foot_stable = self._update_single_joint_stability(RIGHT_FOOT_INDEX, is_left=False)

        # Update heel stability
        left_heel_stable = self._update_single_joint_stability(LEFT_HEEL_INDEX, is_left=True)
        right_heel_stable = self._update_single_joint_stability(RIGHT_HEEL_INDEX, is_left=False)

        self._update_nose_motion_counter()

        # Foot stability for detection (at least one foot stable X&Y)
        self.is_stable_for_detection_foot = left_foot_stable or right_foot_stable
        if self.debug:
            self.logger.debug(f"JumpMovement: Stability for detection FOOT (at least one foot stable X&Y): {self.is_stable_for_detection_foot}")

        # Heel stability for detection (at least one heel stable X&Y)
        self.is_stable_for_detection_heel = left_heel_stable or right_heel_stable
        if self.debug:
            self.logger.debug(f"JumpMovement: Stability for detection HEEL (at least one heel stable X&Y): {self.is_stable_for_detection_heel}")

        # Reset is_in_motion based on FOOT stability
        if self.is_stable_for_detection_foot:
            if self.is_in_motion:
                if self.debug:
                    self.logger.debug("JumpMovement: Resetting is_in_motion because FOOT movement is stable.")
                self.is_in_motion = False

    def detect(self) -> Optional[str]:
        """Detects a jump based on both feet moving upward."""
        if self.is_in_motion or self.is_stable_for_detection_heel or self.motion_counter_nose < self.require_nose_motion_frames:
            if self.debug:
                debug_msg = f"JumpMovement: Detect prevented - "
                if self.is_in_motion: debug_msg += "is_in_motion=True "
                if self.is_stable_for_detection_heel: debug_msg += "is_stable_for_detection_heel=True "
                if self.motion_counter_nose < self.require_nose_motion_frames: debug_msg += f"nose_counter={self.motion_counter_nose}/{self.require_nose_motion_frames}"
                self.logger.debug(debug_msg)
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

        left_heel_distance, left_heel_dir_up = self.analyzer.get_points_distance(LEFT_HEEL_INDEX, Y_COORDINATE_INDEX)
        right_heel_distance, right_heel_dir_up = self.analyzer.get_points_distance(RIGHT_HEEL_INDEX, Y_COORDINATE_INDEX)
        if self.debug:
            self.logger.debug(f"JumpMovement: Left heel diff: {left_heel_distance:.4f}, Right heel diff: {right_heel_distance:.4f} dir_down: {left_heel_dir_up}, {right_heel_dir_up}")

        # Jump is detected when:
        # 1. Not stable for detection (feet are moving)
        # 2. Both feet are moving upward (not dir_down)
        # 3. Both feet distances exceed jump threshold
        if (left_heel_dir_up and right_heel_dir_up and
            left_heel_distance > self.config.jump_threshold and
            right_heel_distance > self.config.jump_threshold):
            
            if self.debug:
                self.logger.debug(f"JumpMovement: Jump detected - Left heel diff: {left_heel_distance:.4f}, Right heel diff: {right_heel_distance:.4f}")
            return JUMP
            
        return None 