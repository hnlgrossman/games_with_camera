from keyboard_controller import trigger_key, hold_key, combo_key, simulate_wasd_movement, simulate_arrow_movement
import time

class GameController:
    def __init__(self):
        """Initialize the game controller."""
        self.use_camera = False
        print("Game controller initialized")
        
    def set_use_camera(self, use_camera):
        """
        Set whether to use camera controls or not.
        For now, this will always be False.
        
        Args:
            use_camera (bool): Whether to use camera controls
        """
        self.use_camera = use_camera
        print(f"Camera controls {'enabled' if use_camera else 'disabled'}")
    
    def press_button(self, button):
        """
        Press a game button (keyboard key).
        
        Args:
            button (str): The button/key to press
        """
        if not self.use_camera:
            trigger_key(button)
            print(f"Pressed button: {button}")
    
    def hold_button(self, button, duration=1.0):
        """
        Hold a game button (keyboard key) for a specified duration.
        
        Args:
            button (str): The button/key to hold
            duration (float): Time in seconds to hold the button
        """
        if not self.use_camera:
            hold_key(button, duration)
            print(f"Held button {button} for {duration} seconds")
    
    def press_combo(self, buttons):
        """
        Press a combination of buttons simultaneously.
        
        Args:
            buttons (list): List of buttons/keys to press
        """
        if not self.use_camera:
            combo_key(buttons)
            print(f"Pressed combo: {buttons}")
    
    def move(self, direction, duration=0.5, control_scheme='wasd'):
        """
        Move in a specified direction.
        
        Args:
            direction (str): Direction to move
            duration (float): Time to hold the movement
            control_scheme (str): 'wasd' or 'arrows'
        """
        if not self.use_camera:
            if control_scheme.lower() == 'wasd':
                simulate_wasd_movement(direction, duration)
            elif control_scheme.lower() == 'arrows':
                simulate_arrow_movement(direction, duration)
            else:
                print(f"Unknown control scheme: {control_scheme}")
            
            print(f"Moved {direction} for {duration} seconds using {control_scheme}")

# Example usage
if __name__ == "__main__":
    controller = GameController()
    
    # Basic controls example
    print("\nTesting basic controls in 2 seconds...")
    time.sleep(2)
    
    controller.press_button('space')  # Jump
    time.sleep(0.5)
    
    controller.hold_button('shift', 0.5)  # Sprint briefly
    time.sleep(0.5)
    
    controller.press_combo(['ctrl', 'c'])  # For example, crouch and shoot
    time.sleep(0.5)
    
    # Movement example
    print("\nTesting movement controls...")
    controller.move('forward', 0.5)  # Move forward
    time.sleep(0.5)
    
    controller.move('right', 0.3)  # Move right
    time.sleep(0.5)
    
    # Using arrow keys
    controller.move('up', 0.5, control_scheme='arrows')
    
    print("\nTest completed!") 