from typing import Optional, Tuple, TYPE_CHECKING, List
from .base_movement import BaseMovement
from ..constants import START_UP, START_DOWN, END_UP, END_DOWN

if TYPE_CHECKING:
    from src.apps.dance_map.movement_analyzer import MovementAnalyzer # To avoid circular import

class LinearMovement(BaseMovement):
    """Detects step movements (left or right)."""

    def __init__(self, analyzer: 'MovementAnalyzer', debug: bool = False):
        super().__init__(analyzer, debug)


    @property
    def detectable_moves(self) -> List[str]:
        """Returns the list of movement types this detector can detect."""
        return [START_UP, START_DOWN, END_UP, END_DOWN]
        
    
    def detect(self) -> Optional[str]:
        """Detects step left or step right."""
        