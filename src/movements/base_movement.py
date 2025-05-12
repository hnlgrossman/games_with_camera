from abc import ABC, abstractmethod
from typing import Optional, Any, List

class BaseMovement(ABC):
    """Abstract base class for movement detection."""

    def __init__(self, analyzer: Any, debug: bool = False):
        self.analyzer = analyzer
        self.config = analyzer.config
        self.logger = analyzer.logger
        self.debug = debug if analyzer.debug else False
        self.is_in_motion: bool = False # Tracks if the movement is currently active

    @abstractmethod
    def update_stability_and_motion_status(self) -> None:
        """
        Updates the stability criteria for the movement.
        If stable, resets the is_in_motion flag.
        """
        pass

    @abstractmethod
    def detect(self) -> Optional[str]:
        """
        Attempts to detect the specific movement.
        Returns the name of the detected movement (e.g., "Step Left", "Jump") or None.
        """
        pass

    @property
    @abstractmethod
    def detectable_moves(self) -> List[str]:
        """
        Returns a list of movement names that this detector can detect.
        This helps for API discoverability and documentation.
        """
        pass
    

    def on_movement_detected(self) -> None:
        """Called by MovementAnalyzer when this movement is detected."""
        self.is_in_motion = True
        if self.debug:
            self.logger.debug(f"{self.__class__.__name__} set to is_in_motion = True")

    def reset_if_stable(self) -> None:
        """
        If the conditions indicate stability (specific to the movement),
        this method should reset is_in_motion.
        This is typically called within update_stability_and_motion_status.
        """
        # This method will be more concretely implemented or used by subclasses
        pass

    @property
    def name(self) -> str:
        """Returns the general name of the movement type (e.g., 'step', 'jump')."""
        return self.__class__.__name__.lower().replace("movement", "") 