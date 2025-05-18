from typing import Optional, Tuple, TYPE_CHECKING, List
from .base_movement import BaseMovement
from src.constants import STEP_RIGHT, STEP_LEFT, FORWARD, BACKWARD

if TYPE_CHECKING:
    from src.apps.dance_map.movement_analyzer import MovementAnalyzer # To avoid circular import

class PressMovement(BaseMovement):
    """Detects step movements (left or right)."""

    def __init__(self, analyzer: 'MovementAnalyzer', debug: bool = False):
        super().__init__(analyzer, debug)
        
        self.last_detected_move = None
        self.last_detection_time = 0

    @property
    def detectable_moves(self) -> List[str]:
        """Returns the list of movement types this detector can detect."""
        return [FORWARD, BACKWARD, STEP_LEFT, STEP_RIGHT]
    
    def detect(self) -> Optional[str]:
        """
        Detects press movements when a foot is in a specific square, is stable,
        and the stable counter is 1 (first frame of stability).
        """
        # Make sure squares are mapped
        if not self.analyzer.has_mapped_squares:
            return None
            
        # Check left foot
        if (self.analyzer.left_foot_stable and 
            self.analyzer.left_foot_stable_counter == 1 and 
            self.analyzer.left_foot_square):
            
            # Detect movement based on which square the foot is in
            if self.analyzer.left_foot_square == "left":
                return STEP_LEFT
            elif self.analyzer.left_foot_square == "right":
                return STEP_RIGHT
            elif self.analyzer.left_foot_square == "forward":
                return FORWARD
            elif self.analyzer.left_foot_square == "backward":
                return BACKWARD
        
        # Check right foot
        if (self.analyzer.right_foot_stable and 
            self.analyzer.right_foot_stable_counter == 1 and 
            self.analyzer.right_foot_square):
            
            # Detect movement based on which square the foot is in
            if self.analyzer.right_foot_square == "left":
                return STEP_LEFT
            elif self.analyzer.right_foot_square == "right":
                return STEP_RIGHT
            elif self.analyzer.right_foot_square == "forward":
                return FORWARD
            elif self.analyzer.right_foot_square == "backward":
                return BACKWARD
        
        return None
       
