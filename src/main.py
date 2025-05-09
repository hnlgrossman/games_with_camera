from config import MovementConfig
from movement_detector import MovementDetector
from triggers import trigger_left, trigger_right
from typing import Dict, Any

def movement_callback(movement: str, data: Dict[str, Any]) -> None:
    """Callback function for movement detection"""
    if movement == "Step Right":
        trigger_right()
        print("right_move")
    elif movement == "Step Left":
        trigger_left()
        print("left_move")

def main():
    detector = MovementDetector(useCamera=False, callback=movement_callback, isTest=False, debug=True)
    video_path = "C:/projects/games_with_camera/src/tests/moves_videos/jump.mp4"
    detector.start_camera(video_path)

if __name__ == "__main__":
    main() 