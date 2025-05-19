from typing import Optional, Tuple, List

from ..constants import START_LEFT, START_RIGHT, END_LEFT, END_RIGHT
from .base_movement import BaseMovement


class AsideMovement(BaseMovement):
    """Detects step movements (left or right)."""

    def __init__(self, analyzer: 'MovementAnalyzer', debug: bool = False):
        super().__init__(analyzer, debug)

        

    @property
    def detectable_moves(self) -> List[str]:
        """Returns the list of movement types this detector can detect."""
        return [START_RIGHT, START_LEFT, END_RIGHT, END_LEFT]
        
    
    def detect(self) -> Optional[str]:
        pass