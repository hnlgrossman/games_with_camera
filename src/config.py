from dataclasses import dataclass
from typing import Optional

@dataclass
class MovementConfig:
    """Configuration parameters for movement detection"""
    min_detection_confidence: float = 0.5
    min_tracking_confidence: float = 0.5
    required_stable_frames_per_30_fps: int = 4
    jump_threshold: float = 0.005
    step_threshold: float = 0.04
    bend_threshold: float = 0.06
    cooldown_period: float = 1.0
    stability_threshold: float = 0.028
    stability_moves_threshold = {"jump": 0.01, "bend": 0.01}
    num_frames_to_check: int = 5
    camera_index: int = 1  # Camera device index to use 
    visibility_threshold: float = 0.5  # Minimum visibility score for landmarks to be considered
    sound_enabled: bool = False  # Whether to play movement sounds
    sound_volume: float = 0.7  # Sound volume level (0.0 to 1.0)
    log_file_path: Optional[str] = None  # Path to log file, if None logging goes to console

    # New parameters for base_height calculation
    straight_pose_x_spread_threshold: float = 0.15  # Max horizontal spread for key points to be 'straight'
    stillness_threshold: float = 0.03  # Max normalized movement of nose for 'stillness'
    min_base_height_threshold: float = 0.4 # Min normalized y-distance (nose to feet) for valid height

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
            raise ValueError("num_frames_to_check must be at least 1 (ideally >=2 for stillness check)")
        if self.camera_index < 0:
            raise ValueError("camera_index must be non-negative")
        if self.visibility_threshold < 0 or self.visibility_threshold > 1:
            raise ValueError("visibility_threshold must be between 0 and 1")
        if self.sound_volume < 0 or self.sound_volume > 1:
            raise ValueError("sound_volume must be between 0 and 1")
        
        # Validations for new parameters
        if not (0 < self.straight_pose_x_spread_threshold < 1):
            raise ValueError("straight_pose_x_spread_threshold must be between 0 and 1")
        if not (0 < self.stillness_threshold < 1):
            raise ValueError("stillness_threshold must be between 0 and 1")
        if not (0 < self.min_base_height_threshold < 1):
            raise ValueError("min_base_height_threshold must be between 0 and 1") 