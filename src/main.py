import os
from config import MovementConfig
from movement_detector import MovementDetector
from src.constants import STEP_LEFT, STEP_RIGHT, FORWARD, BACKWARD, JUMP, BEND
from triggers import trigger_left, trigger_right, trigger_up, trigger_down
from typing import Dict, Any
import logging
from logger import setup_logging

def movement_callback(movement: str, data: Dict[str, Any]) -> None:
    """Callback function for movement detection"""
    logger = logging.getLogger('MovementCallback')
    if movement == STEP_RIGHT:
        trigger_right()
        logger.info("right_move")
    elif movement == STEP_LEFT:
        trigger_left()
        logger.info("left_move")
    elif movement == FORWARD or movement == JUMP:
        trigger_up()
        logger.info("forward_move")
    elif movement == BACKWARD or movement == BEND:
        trigger_down()
        logger.info("backward_move")


def main():
    print(os.getenv("APP_NAME"))
    # Create config with log file path
    config = MovementConfig(
        # log_file_path="C:/projects/games_with_camera/moves_logs/multi jump.log",  # Log file will be created in the specified directory
        sound_enabled=True,
        sound_volume=0.7,
        app_name=os.getenv("APP_NAME")
    )
    # Set up logging first
    setup_logging(config.log_file_path, debug=True)
    logger = logging.getLogger('Main')
    logger.info("Main logger: Starting movement detection")
    
    # Create detector with debug mode enabled
    detector = MovementDetector(
        config=config,
        useCamera=False,
        callback=movement_callback,
        isTest=False,
        debug=True
    )
    
    # video_path = "recorded_setions/rec_20250512_213129.mp4"
    # video_path = "src/tests/moves_videos/jump_and_fast_left.mp4"
    # video_path = "src/tests/moves_videos/test_1.mp4"
    # video_path = "src/tests/moves_videos/jump.mp4"
    # video_path = "src/tests/moves_videos/multy_jump_2.mp4"
    # video_path = "src/tests/moves_videos/multy_bend_2.mp4"
    video_path = "src/tests/moves_videos/dance_map.mp4"
    # video_path = "src/tests/moves_videos/check-z-with-jump.mp4"
    
    try:
        logger.info("Main logger: Calling detector.start_camera()")
        detector.start_camera(video_path)
    except Exception as e:

        logger.exception("Main logger: An error occurred during detector.start_camera()")
    finally:
        logger.info("Main logger: Program ending, shutting down logging.")
        logging.shutdown()

if __name__ == "__main__":
    print("Starting main")
    main() 