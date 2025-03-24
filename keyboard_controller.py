import keyboard
import time

def trigger_key(key):
    """
    Trigger a keyboard key press and release.
    
    Args:
        key (str): The key to press (e.g., 'a', 'space', 'enter')
    """
    keyboard.press(key)
    time.sleep(0.1)  # Short delay to ensure the key press is registered
    keyboard.release(key)
    
def hold_key(key, duration=1.0):
    """
    Hold a keyboard key for a specified duration.
    
    Args:
        key (str): The key to hold (e.g., 'w', 'up', 'shift')
        duration (float): Time in seconds to hold the key
    """
    keyboard.press(key)
    time.sleep(duration)
    keyboard.release(key)
    
def combo_key(keys):
    """
    Press multiple keys simultaneously (e.g., for combo moves).
    
    Args:
        keys (list): List of keys to press simultaneously
    """
    for key in keys:
        keyboard.press(key)
    
    time.sleep(0.1)  # Short delay
    
    for key in keys:
        keyboard.release(key)

def simulate_wasd_movement(direction, duration=0.5):
    """
    Simulate WASD movement for a specified direction.
    
    Args:
        direction (str): Direction to move ('forward', 'backward', 'left', 'right')
        duration (float): Time in seconds to hold the key
    """
    key_mapping = {
        'forward': 'w',
        'backward': 's',
        'left': 'a',
        'right': 'd'
    }
    
    if direction in key_mapping:
        hold_key(key_mapping[direction], duration)
    else:
        print(f"Unknown direction: {direction}")

def simulate_arrow_movement(direction, duration=0.5):
    """
    Simulate arrow key movement for a specified direction.
    
    Args:
        direction (str): Direction to move ('up', 'down', 'left', 'right')
        duration (float): Time in seconds to hold the key
    """
    key_mapping = {
        'up': 'up',
        'down': 'down',
        'left': 'left',
        'right': 'right'
    }
    
    if direction in key_mapping:
        hold_key(key_mapping[direction], duration)
    else:
        print(f"Unknown direction: {direction}")

# Example of usage
if __name__ == "__main__":
    print("Keyboard controller loaded")
    print("Press Ctrl+C to exit")
    
    try:
        # Example: Press spacebar after 2 seconds
        print("Pressing spacebar in 2 seconds...")
        time.sleep(2)
        trigger_key('space')
        
        # Example: Hold the 'W' key for 1 second
        print("Holding 'W' key for 1 second...")
        time.sleep(1)
        hold_key('w', 1.0)
        
        # Example: Press Shift+W for a sprint
        print("Pressing Shift+W combo...")
        time.sleep(1)
        combo_key(['shift', 'w'])
        
    except KeyboardInterrupt:
        print("Keyboard controller stopped") 