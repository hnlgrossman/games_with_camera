from config import MovementConfig
from movement_detector import MovementDetector
from triggers import trigger_left, trigger_right

def right_move(_):
    trigger_right()
    print("right_move")
    

def left_move(_):
    trigger_left()
    print("left_move")

def main():
    moves = {"right_move": right_move, "left_move": left_move}
    detector = MovementDetector(useCamera=False, moves=moves, isTest=False, debug=True)
    video_path = "C:/projects/games_with_camera/src/tests/moves_videos/test_1.mp4"
    detector.start_camera(video_path)

if __name__ == "__main__":
    main() 