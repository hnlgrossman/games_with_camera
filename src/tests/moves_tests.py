import json
import sys
import os

# Add the parent directory to the path to import modules from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from movement_detector import MovementDetector
from config import MovementConfig


def run_movement_tests():
    # Load the test configuration
    with open(os.path.join(os.path.dirname(__file__), 'tests.json'), 'r') as file:
        test_config = json.load(file)
    
    # Prompt user for specific test name
    test_to_run = input("Enter a specific test name to run (leave blank to run all tests): ").strip()
    
    # Filter tests based on user input
    if test_to_run:
        if test_to_run in test_config:
            test_items = {test_to_run: test_config[test_to_run]}
            print(f"Running only test: {test_to_run}")
        else:
            print(f"Test '{test_to_run}' not found. Available tests: {', '.join(test_config.keys())}")
            return
    else:
        test_items = test_config
        print("Running all tests")
    
    # Test each scenario defined in the JSON file
    for test_name, test_data in test_items.items():
        print(f"\nRunning test: {test_name}")
        # Resolve the video path relative to the test directory
        video_path = os.path.abspath(os.path.join(os.path.dirname(__file__), test_data["video_path"]))
        expected_moves = test_data["moves"]
        
        print(f"Using video path: {video_path}")
        
        # Create a dictionary to store the detected moves
        detected_moves = []
        
        # Define move handlers that will record when they're called
        def right_move(data):
            detected_moves.append({
                "move_key": "step_right", 
                "frame": data["frame"]
            })
            print(f"Right move detected at frame {data['frame']}")
        
        def left_move(data):
            detected_moves.append({
                "move_key": "step_left", 
                "frame": data["frame"]
            })
            print(f"Left move detected at frame {data['frame']}")
        
        def jump_move(data):
            detected_moves.append({
                "move_key": "jump", 
                "frame": data["frame"]
            })
            print(f"Jump detected at frame {data['frame']}")
        
        # Map of move keys to handler functions
        move_handlers = {
            "right_move": right_move,
            "left_move": left_move, 
            "jump": jump_move
        }
        
        # Create and run the movement detector
        detector = MovementDetector(
            useCamera=False,
            moves=move_handlers,
            isTest=True
        )
        
        # Process the video
        detector.start_camera(video_path)
        
        # Verify the results
        print(f"Expected moves: {expected_moves}")
        print(f"Detected moves: {detected_moves}")
        
        # Check that we have the same number of moves
        if len(expected_moves) != len(detected_moves):
            print(f"❌ FAIL: Expected {len(expected_moves)} moves but detected {len(detected_moves)}")
            continue
        else:
            print(f"✓ PASS: Detected correct number of moves: {len(detected_moves)}")
        
        # Check that each move was detected in the correct order and frame range
        all_passed = True
        for i, expected_move in enumerate(expected_moves):
            detected = detected_moves[i]
            
            # Check move type
            expected_key = expected_move["move_key"]
            mapping = {
                "step_right": "step_right",
                "step_left": "step_left",
                "jump": "jump"
            }
            
            if mapping[expected_key] != detected["move_key"]:
                print(f"❌ FAIL: Move {i+1} should be {expected_key} but was {detected['move_key']}")
                all_passed = False
            
            # Check frame range if specified
            if "from_frame" in expected_move and "to_frame" in expected_move:
                if detected["frame"] < expected_move["from_frame"]:
                    print(f"❌ FAIL: Move {expected_key} detected too early at frame {detected['frame']}")
                    all_passed = False
                
                if detected["frame"] > expected_move["to_frame"]:
                    print(f"❌ FAIL: Move {expected_key} detected too late at frame {detected['frame']}")
                    all_passed = False
        
        if all_passed:
            print(f"✓ PASS: All move validations passed for test: {test_name}")
        else:
            print(f"❌ FAIL: Some move validations failed for test: {test_name}")


if __name__ == "__main__":
    run_movement_tests()
