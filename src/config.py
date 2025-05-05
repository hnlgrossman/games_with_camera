from dataclasses import dataclass

@dataclass
class MovementConfig:
    """Configuration parameters for movement detection"""
    min_detection_confidence: float = 0.5
    min_tracking_confidence: float = 0.5
    required_stable_frames: int = 4
    jump_threshold: float = 0.025
    step_threshold: float = 0.02
    bend_threshold: float = 0.1
    cooldown_period: float = 1.0
    stability_threshold: float = 0.028
    num_frames_to_check: int = 5 