from typing import Optional, TYPE_CHECKING, List, Tuple
from .base_movement import BaseMovement
import mediapipe as mp
from src.constants import Y_COORDINATE_INDEX, LEFT_SHOULDER_INDEX, RIGHT_SHOULDER_INDEX

if TYPE_CHECKING:
    from src.movement_analyzer import MovementAnalyzer # To avoid circular import

class BendMovement(BaseMovement):
    """Detects bend movements."""

    def __init__(self, analyzer: 'MovementAnalyzer'):
        super().__init__(analyzer)

        # Stability counters and flags
        self.stable_counter_left_shoulder: int = 0
        self.stable_counter_right_shoulder: int = 0
        self.is_left_shoulder_stable_y: bool = True
        self.is_right_shoulder_stable_y: bool = True

        # Motion state
        self.is_stable_for_detection: bool = True # Analogous to old is_stable_move["bend"]

    @property
    def detectable_moves(self) -> List[str]:
        """Returns the list of movement types this detector can detect."""
        return ["Bend"]

    def _update_single_shoulder_stability(self, is_left_shoulder: bool) -> bool:
        """Updates stability for a single shoulder and returns its stability status."""
        shoulder_index = LEFT_SHOULDER_INDEX if is_left_shoulder else RIGHT_SHOULDER_INDEX
        shoulder_distance, _ = self.analyzer.get_points_distance(shoulder_index, Y_COORDINATE_INDEX)
        
        counter_name = "left shoulder" if is_left_shoulder else "right shoulder"
        current_counter = self.stable_counter_left_shoulder if is_left_shoulder else self.stable_counter_right_shoulder
        
        required_frames = self.get_required_stable_frames()

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

    def update_stability_and_motion_status(self) -> None:
        """Updates shoulders stability on Y axis and determines if a new bend detection can occur."""
        self._update_single_shoulder_stability(is_left_shoulder=True)
        self._update_single_shoulder_stability(is_left_shoulder=False)

        # Bend is stable for detection only when both shoulders are stable
        self.is_stable_for_detection = self.is_left_shoulder_stable_y and self.is_right_shoulder_stable_y
        
        if self.debug:
            self.logger.debug(f"BendMovement: Stability for detection (both shoulders stable): {self.is_stable_for_detection}")

        if self.is_stable_for_detection:
            if self.is_in_motion:
                if self.debug:
                    self.logger.debug("BendMovement: Resetting is_in_motion because movement is stable.")
                self.is_in_motion = False

    def detect(self) -> Optional[str]:
        """Detects a bend based on both shoulders moving downward."""
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
        is_bend_detected = not self.is_stable_for_detection and not is_left_shoulder_moving_up and not is_right_shoulder_moving_up and left_shoulder_distance > self.config.bend_threshold and right_shoulder_distance > self.config.bend_threshold
        if self.debug:
            self.logger.debug(f"BendMovement: shuld Bend detected: {is_bend_detected}")
        if (is_bend_detected):
            
            if self.debug:
                self.logger.debug(f"BendMovement: Bend detected - Left shoulder diff: {left_shoulder_distance:.4f}, Right shoulder diff: {right_shoulder_distance:.4f}")
            return "Bend"
            
        return None