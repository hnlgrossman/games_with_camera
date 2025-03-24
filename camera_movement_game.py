import cv2
import time
from movement_detector import MovementDetector

def main():
    print("====================================")
    print("Camera Movement Detection System")
    print("====================================")
    print("This program will detect the following movements:")
    print("  - Jump")
    print("  - Step Left")
    print("  - Step Right")
    print("  - Bend")
    print("\nStand in front of the camera and remain still to establish a baseline.")
    print("Press ESC to exit.")
    print("\nInitializing camera...")
    
    try:
        detector = MovementDetector()
        detector.start_camera()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure your camera is connected and working")
        print("2. Check that you have the required libraries installed")
        print("3. Ensure you have adequate lighting for movement detection")

if __name__ == "__main__":
    main() 