from config import MovementConfig
from movement_detector import MovementDetector
from triggers import trigger_left, trigger_right, trigger_up, trigger_down
from typing import Dict, Any
import logging
from logger import setup_logging
import datetime  # Added import
from gui_utils import welcome_screen # ADDED: Import the welcome screen function
import os
from src.constants import STEP_LEFT, STEP_RIGHT, JUMP, BEND, FORWARD, BACKWARD
from importlib import import_module

def movement_callback(movement: str, data: Dict[str, Any]) -> None:
    """Callback function for movement detection"""
    logger = logging.getLogger('MovementCallback')
    if movement == STEP_RIGHT:
        trigger_right()
        logger.info("right_move")
    elif movement == STEP_LEFT:
        trigger_left()
        logger.info("left_move")
    elif movement == JUMP or movement == FORWARD:
        trigger_up()
        logger.info("jump_move")
    elif movement == BEND or movement == BACKWARD:
        trigger_down()
        logger.info("bend_move")

def main():
    # Date check
    if datetime.date.today() > datetime.date(2025, 6, 13):
        print("Error")
        return  # Exit the program

    # Show welcome screen and get user configuration
    # print("Loading welcome screen...") # ADDED: Info message
    # # This will open a new window for camera selection.
    # user_choices = welcome_screen() 

    # # Handle if the user quit the welcome screen or no camera was selected/found
    # if user_choices is None or user_choices[0] is None:
    #     print("Setup cancelled or no camera selected. Exiting program.")
    #     # Ensure any OpenCV windows opened by welcome_screen are closed if not already.
    #     # welcome_screen should handle its own windows, but this is a safeguard.
    #     # import cv2 # Already imported in gui_utils, but explicit here if needed.
    #     # cv2.destroyAllWindows() # welcome_screen should do this.
    #     input("Press Enter to exit...") # Keep console open to see messages
    #     return

    # selected_camera_index, sound_enabled_choice = user_choices

    # Create config with user's choices from the welcome screen
    config = MovementConfig(
        # camera_index=selected_camera_index,      # MODIFIED: Use selected camera
        # sound_enabled=sound_enabled_choice,  # MODIFIED: Use selected sound preference
        camera_index=1,      # MODIFIED: Use selected camera
        sound_enabled=True,  # MODIFIED: Use selected sound preference
        # log_file_path="C:/projects/games_with_camera/moves_logs/multi jump.log",  # Log file will be created in the specified directory
        sound_volume=0.7, # Default sound volume, not configured by welcome screen currently
        app_name=os.environ.get("APP_NAME")
    )
    # Set up logging first
    setup_logging(config.log_file_path, debug=True)
    logger = logging.getLogger('Main')
    logger.info("Main logger: Starting movement detection")
    
    if config.app_name == "wheel":
        movement_callback = import_module(f"src.apps.{config.app_name}.triggers").movement_callback
    # else:
    #     movement_callback = movement_callback

    print(config)
    # Create detector with debug mode enabled
    detector = MovementDetector(
        config=config,
        useCamera=True,
        callback=movement_callback,
        isTest=False,
        debug=True
    )
    
    video_path = "./recorded_setions/rec_20250525_210553.mp4"
    # video_path = "C:/projects/games_with_camera/src/tests/moves_videos/jump_and_fast_left.mp4"
    # video_path = "C:/projects/games_with_camera/src/tests/moves_videos/test_1.mp4"
    # video_path = "C:/projects/games_with_camera/src/tests/moves_videos/jump.mp4"
    # video_path = "C:/projects/games_with_camera/src/tests/moves_videos/multy_jump_2.mp4"
    # video_path = "C:/projects/games_with_camera/src/tests/moves_videos/multy_bend_2.mp4"
    # video_path = "C:/projects/games_with_camera/src/tests/moves_videos/mix_2.mp4"
    # video_path = "C:/projects/games_with_camera/src/tests/moves_videos/check-z-with-jump.mp4"
    
    try:
        logger.info("Main logger: Calling detector.start_camera()")
        detector.start_camera(video_path)
    except Exception as e:
        # Ensure the logger is available or use print for critical errors if logger failed
        if 'logger' in locals():
            logger.exception("Main logger: An error occurred during detector.start_camera()")
        else:
            print(f"CRITICAL ERROR before logger init or during start_camera: {e}")

    finally:
        if 'logger' in locals(): # ADDED: Check if logger was initialized
            logger.info("Main logger: Program ending, shutting down logging.")
            logging.shutdown()
        
        # This print might not be visible if terminal closes immediately after error in some IDEs.
        # The input() below helps keep it open.
        # print(f"AN ERROR OCCURRED: {e}") # Variable e might not be defined if no exception in try block

        import traceback # Keep traceback for any unhandled exit
        traceback.print_exc() # Print full traceback if an exception occurred and wasn't caught
        
        print("Program finished or error occurred.") # MODIFIED: General message
        input("Press Enter to exit...") # Ensure console stays open

if __name__ == "__main__":
    print("Starting main")
    main() 