from dataclasses import dataclass

@dataclass
class MovementConfig:
    """Configuration parameters for movement detection"""
    min_detection_confidence: float = 0.5
    min_tracking_confidence: float = 0.5
    required_stable_frames_per_30_fps: int = 4
    jump_threshold: float = 0.025
    step_threshold: float = 0.02
    bend_threshold: float = 0.1
    cooldown_period: float = 1.0
    stability_threshold: float = 0.028
    num_frames_to_check: int = 5
    camera_index: int = 1  # Camera device index to use 
    visibility_threshold: float = 0.5  # Minimum visibility score for landmarks to be considered

    def __post_init__(self):
        if self.min_detection_confidence < 0 or self.min_detection_confidence > 1:
            raise ValueError("min_detection_confidence must be between 0 and 1")
        if self.min_tracking_confidence < 0 or self.min_tracking_confidence > 1:
            raise ValueError("min_tracking_confidence must be between 0 and 1")
        if self.required_stable_frames_per_30_fps < 1:
            raise ValueError("required_stable_frames_per_30_fps must be at least 1")
        if self.jump_threshold < 0 or self.jump_threshold > 1:
            raise ValueError("jump_threshold must be between 0 and 1")
        if self.step_threshold < 0 or self.step_threshold > 1:
            raise ValueError("step_threshold must be between 0 and 1")
        if self.bend_threshold < 0 or self.bend_threshold > 1:
            raise ValueError("bend_threshold must be between 0 and 1")
        if self.cooldown_period < 0:
            raise ValueError("cooldown_period must be non-negative")
        if self.stability_threshold < 0 or self.stability_threshold > 1:
            raise ValueError("stability_threshold must be between 0 and 1")
        if self.num_frames_to_check < 1:
            raise ValueError("num_frames_to_check must be at least 1")
        if self.camera_index < 0:
            raise ValueError("camera_index must be non-negative")
        if self.visibility_threshold < 0 or self.visibility_threshold > 1:
            raise ValueError("visibility_threshold must be between 0 and 1") 