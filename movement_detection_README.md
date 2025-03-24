# Camera Movement Detection System

This Python application uses computer vision to detect specific body movements through your webcam, including:
- Jump
- Step Left
- Step Right
- Bend

## Requirements

- Python 3.7 or higher
- Webcam
- Sufficient lighting for proper detection

## Installation

1. Clone this repository or download the files:
   - `movement_detector.py`
   - `camera_movement_game.py`
   - `requirements.txt`

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python camera_movement_game.py
   ```

2. When the application starts:
   - Stand in front of your camera
   - Remain still for a few seconds to establish a baseline position
   - Once "Reference position established" appears in the console, you can start making movements
   - The detected movement will be displayed on the screen
   - Press ESC to exit the application

## How It Works

This application uses:
- OpenCV for video capture and display
- MediaPipe for human pose estimation
- Custom algorithms to detect specific movements based on body key points

## Troubleshooting

If you encounter issues:
1. Ensure your webcam is properly connected and functioning
2. Check that lighting is adequate for the camera to clearly see you
3. Make sure you're standing far enough from the camera (about 6-8 feet)
4. Verify that all required libraries are installed correctly

## Adjusting Sensitivity

If the movement detection is too sensitive or not sensitive enough, you can modify the following parameters in `movement_detector.py`:
- `jump_threshold`: Threshold for jump detection (default: 0.1)
- `step_threshold`: Threshold for side step detection (default: 0.1)
- `bend_threshold`: Threshold for bend detection (default: 0.2)
- `cooldown_period`: Time in seconds between detections (default: 1.0) 