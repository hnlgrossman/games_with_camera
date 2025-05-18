from typing import Optional, Tuple, TYPE_CHECKING, List
from .base_movement import BaseMovement
from src.constants import LEFT_FOOT_INDEX, RIGHT_FOOT_INDEX, Z_COORDINATE_INDEX, STEP_RIGHT, STEP_LEFT, FORWARD, BACKWARD

if TYPE_CHECKING:
    from src.apps.dance_map.movement_analyzer import MovementAnalyzer # To avoid circular import

class LinearMovement(BaseMovement):
    """Detects step movements (left or right)."""

    def __init__(self, analyzer: 'MovementAnalyzer', debug: bool = False):
        super().__init__(analyzer, debug)

        self.linear_threshold = 0.06
        

    @property
    def detectable_moves(self) -> List[str]:
        """Returns the list of movement types this detector can detect."""
        return [FORWARD, BACKWARD]
    
    def _detect_linear_move(self, foot_distance: float, foot_is_forward: bool, is_left_foot: bool) -> Optional[str]:
        if self.analyzer.foots_distance < self.analyzer.foots_distance_linear_threshold:
            return None

        if(is_left_foot):
            if self.analyzer.is_left_foot_forward and foot_is_forward:
                return FORWARD
            else:
                return BACKWARD
        else:
            if self.analyzer.is_left_foot_forward and not foot_is_forward:
                return BACKWARD
            else:
                return FORWARD
    
    def detect(self) -> Optional[str]:
        """Detects step left or step right."""
        if self.is_in_motion or self.analyzer.is_general_stable: # If already stepping, don't detect another step
            return None

        # Step Right Detection
        right_foot_distance, right_foot_is_forward = self.analyzer.get_points_distance(RIGHT_FOOT_INDEX, Z_COORDINATE_INDEX)
        left_foot_distance, left_foot_is_forward = self.analyzer.get_points_distance(LEFT_FOOT_INDEX, Z_COORDINATE_INDEX)

        if right_foot_distance > self.linear_threshold and right_foot_distance > left_foot_distance:
            return self._detect_linear_move(right_foot_distance, right_foot_is_forward, is_left_foot=False)
        elif left_foot_distance > self.linear_threshold and left_foot_distance > right_foot_distance:
            return self._detect_linear_move(left_foot_distance, left_foot_is_forward, is_left_foot=True)
        else:
            return None
       
