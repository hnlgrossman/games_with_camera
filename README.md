# Game Controller with Keyboard Triggers

A Python-based game controller that allows controlling games using keyboard triggers. Future implementation will include camera-based control.

## Features

- Basic keyboard controls (press, hold, release)
- Combination key presses
- Directional controls using WASD or arrow keys
- Ready for future camera control integration

## Installation

1. Clone this repository
2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Example

```python
from game_controller import GameController

# Create a controller instance
controller = GameController()

# Press a single button
controller.press_button('space')  # Jump

# Hold a button for a duration
controller.hold_button('shift', 1.0)  # Sprint for 1 second

# Press a combination of buttons
controller.press_combo(['ctrl', 'c'])  # Example: crouch and shoot

# Move in a direction using WASD controls
controller.move('forward', 0.5)  # Move forward for 0.5 seconds

# Move using arrow keys
controller.move('right', 0.3, control_scheme='arrows')
```

### Running the Demo

To test the controller, run:

```bash
python game_controller.py
```

## Notes

- This version only includes keyboard controls, without camera integration
- The `keyboard` library requires admin privileges on some systems
- On Windows, you may need to run your Python script as administrator
- Future versions will include camera-based control options

## Requirements

- Python 3.6+
- keyboard 0.13.5+ 