from typing import Optional, Tuple, TYPE_CHECKING, List
from .base_movement import BaseMovement
from src.constants import LEFT_FOOT_INDEX, RIGHT_FOOT_INDEX, X_COORDINATE_INDEX, STEP_RIGHT, STEP_LEFT

if TYPE_CHECKING:
    from src.apps.original.movement_analyzer import MovementAnalyzer # To avoid circular import

class StepMovement(BaseMovement):
    """Detects step movements (left or right)."""

    def __init__(self, analyzer: 'MovementAnalyzer', debug: bool = False):
        super().__init__(analyzer, debug)

        # Stability counters and flags
        self.stable_counter_left_foot: int = 0
        self.stable_counter_right_foot: int = 0
        self.is_left_foot_stable_x: bool = True
        self.is_right_foot_stable_x: bool = True

        self.get_required_stable_frames = 3
        
        # Motion state
        self.is_stable_for_detection: bool = True # Analogous to old is_stable_move["step"]

    @property
    def detectable_moves(self) -> List[str]:
        """Returns the list of movement types this detector can detect."""
        return [STEP_LEFT, STEP_RIGHT]

    def _update_single_foot_stability(self, is_left_foot: bool) -> bool:
        """Updates stability for a single foot and returns its stability status."""
        foot_index = LEFT_FOOT_INDEX if is_left_foot else RIGHT_FOOT_INDEX
        foot_distance, _ = self.analyzer.get_points_distance(foot_index, X_COORDINATE_INDEX)
        
        counter_name = "left foot" if is_left_foot else "right foot"
        current_counter = self.stable_counter_left_foot if is_left_foot else self.stable_counter_right_foot
        
        required_frames = self.get_required_stable_frames

        if foot_distance < self.config.stability_threshold:
            current_counter += 1
            if self.debug:
                self.logger.debug(f"StepMovement: {counter_name.title()} stability counter: {current_counter}/{required_frames}")
            is_stable = current_counter >= required_frames
        else:
            if self.debug and current_counter > 0:
                self.logger.debug(f"StepMovement: Reset {counter_name} stability counter. Distance: {foot_distance:.4f}")
            current_counter = 0
            is_stable = False
            
        if is_left_foot:
            self.stable_counter_left_foot = current_counter
            self.is_left_foot_stable_x = is_stable
        else:
            self.stable_counter_right_foot = current_counter
            self.is_right_foot_stable_x = is_stable
        return is_stable

    def _determine_stability_criterion(self, left_foot_distance: float, left_foot_is_left: bool,
                                     right_foot_distance: float, right_foot_is_left: bool) -> Tuple[bool, str]:
        """Determines which foot's stability criterion to use."""
        # This logic is preserved from the original MovementAnalyzer
        if not right_foot_is_left and right_foot_distance > left_foot_distance:
            return self.is_right_foot_stable_x, "is_right_foot_stable_x"
        elif left_foot_is_left and left_foot_distance > right_foot_distance:
            return self.is_left_foot_stable_x, "is_left_foot_stable_x"
        else:
            if self.stable_counter_right_foot > self.stable_counter_left_foot:
                return self.is_right_foot_stable_x, "is_right_foot_stable_x"
            else:
                return self.is_left_foot_stable_x, "is_left_foot_stable_x"

    def update_stability_and_motion_status(self) -> None:
        """Updates foot stability and determines if a new step detection can occur."""
        self._update_single_foot_stability(is_left_foot=True)
        self._update_single_foot_stability(is_left_foot=False)

        # Update is_stable_for_detection based on current foot movements
        left_foot_distance, left_foot_is_left = self.analyzer.get_points_distance(LEFT_FOOT_INDEX, X_COORDINATE_INDEX)
        right_foot_distance, right_foot_is_left = self.analyzer.get_points_distance(RIGHT_FOOT_INDEX, X_COORDINATE_INDEX)

        self.is_stable_for_detection, stable_check_name = self._determine_stability_criterion(
            left_foot_distance, left_foot_is_left,
            right_foot_distance, right_foot_is_left
        )
        
        if self.debug:
            self.logger.debug(f"StepMovement: Stability criterion for detection: {stable_check_name} -> {self.is_stable_for_detection}")

        if self.is_stable_for_detection:
            if self.is_in_motion:
                if self.debug:
                    self.logger.debug("StepMovement: Resetting is_in_motion because movement is stable.")
                self.is_in_motion = False
    
    def detect(self) -> Optional[str]:
        """Detects step left or step right."""
        if self.is_in_motion or self.is_stable_for_detection: # If already stepping, don't detect another step
            return None

        # Step Right Detection
        right_foot_distance, right_foot_is_left = self.analyzer.get_points_distance(RIGHT_FOOT_INDEX, X_COORDINATE_INDEX)
        left_foot_distance, left_foot_is_left = self.analyzer.get_points_distance(LEFT_FOOT_INDEX, X_COORDINATE_INDEX)

        if self.debug:
            self.logger.debug(f"StepMovement: Left foot distance: {left_foot_distance:.4f}, direction left: {left_foot_is_left}")
            self.logger.debug(f"StepMovement: Right foot distance: {right_foot_distance:.4f}, direction left: {right_foot_is_left}")
        if not right_foot_is_left and right_foot_distance > self.config.step_threshold:
            # Check if this detection aligns with the dominant unstable foot from _determine_stability_criterion
            # This is a simplified check; _determine_stability_criterion primarily influences is_stable_for_detection
            _, stability_criterion_name = self._determine_stability_criterion(
                left_foot_distance, left_foot_is_left,
                right_foot_distance, right_foot_is_left
            )
            if "right_foot" in stability_criterion_name or self.stable_counter_left_foot == 0 : # Favor if right foot is the one less stable or if left is completely stable
                if self.debug:
                    self.logger.debug(f"StepMovement: Step Right detected - Diff: {right_foot_distance:.4f}")
                return STEP_RIGHT

        # Step Left Detection
        
        if left_foot_is_left and left_foot_distance > self.config.step_threshold:
            _, stability_criterion_name = self._determine_stability_criterion(
                left_foot_distance, left_foot_is_left,
                self.analyzer.get_points_distance(RIGHT_FOOT_INDEX, X_COORDINATE_INDEX)[0],
                self.analyzer.get_points_distance(RIGHT_FOOT_INDEX, X_COORDINATE_INDEX)[1]
            )
            if "left_foot" in stability_criterion_name or self.stable_counter_right_foot == 0: # Favor if left foot is the one less stable or if right is completely stable
                if self.debug:
                    self.logger.debug(f"StepMovement: Step Left detected - Diff: {left_foot_distance:.4f}")
                return STEP_LEFT
                
        return None 