import vgamepad as vg
import time
import threading
import sys

# Define common button names for easier mapping
# Xbox Buttons
XBOX_BUTTON_A = "A"
XBOX_BUTTON_B = "B"
XBOX_BUTTON_X = "X"
XBOX_BUTTON_Y = "Y"
XBOX_BUTTON_LB = "LB"
XBOX_BUTTON_RB = "RB"
XBOX_BUTTON_LS = "LS"  # Left stick press
XBOX_BUTTON_RS = "RS"  # Right stick press
XBOX_BUTTON_START = "START"
XBOX_BUTTON_BACK = "BACK"
XBOX_BUTTON_DPAD_UP = "DPAD_UP"
XBOX_BUTTON_DPAD_DOWN = "DPAD_DOWN"
XBOX_BUTTON_DPAD_LEFT = "DPAD_LEFT"
XBOX_BUTTON_DPAD_RIGHT = "DPAD_RIGHT"

# DS4 Buttons
DS4_BUTTON_CROSS = "CROSS"
DS4_BUTTON_CIRCLE = "CIRCLE"
DS4_BUTTON_SQUARE = "SQUARE"
DS4_BUTTON_TRIANGLE = "TRIANGLE"
DS4_BUTTON_L1 = "L1"
DS4_BUTTON_R1 = "R1"
DS4_BUTTON_L3 = "L3"  # Left stick press
DS4_BUTTON_R3 = "R3"  # Right stick press
DS4_BUTTON_OPTIONS = "OPTIONS"
DS4_BUTTON_SHARE = "SHARE" # Or Create on newer controllers
DS4_BUTTON_PS = "PS"
DS4_BUTTON_TOUCHPAD = "TOUCHPAD"
DS4_DPAD_UP = "DPAD_UP"
DS4_DPAD_DOWN = "DPAD_DOWN"
DS4_DPAD_LEFT = "DPAD_LEFT"
DS4_DPAD_RIGHT = "DPAD_RIGHT"
DS4_DPAD_NONE = "DPAD_NONE"


class Controller:
    """Manages a virtual gamepad (Xbox 360 or DS4)."""

    def __init__(self, controller_type="xbox360"):
        """Initialize the virtual controller.

        Args:
            controller_type: Type of controller to emulate ("xbox360" or "ds4").
        """
        self.controller_type = controller_type.lower()
        if self.controller_type == "xbox360":
            self.gamepad = vg.VX360Gamepad()
            self.is_xbox = True
            self._button_map = {
                XBOX_BUTTON_A: vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
                XBOX_BUTTON_B: vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
                XBOX_BUTTON_X: vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
                XBOX_BUTTON_Y: vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
                XBOX_BUTTON_LB: vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
                XBOX_BUTTON_RB: vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
                XBOX_BUTTON_LS: vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
                XBOX_BUTTON_RS: vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB,
                XBOX_BUTTON_START: vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
                XBOX_BUTTON_BACK: vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
                XBOX_BUTTON_DPAD_UP: vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
                XBOX_BUTTON_DPAD_DOWN: vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
                XBOX_BUTTON_DPAD_LEFT: vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
                XBOX_BUTTON_DPAD_RIGHT: vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
            }
            self._dpad_map = {
                DS4_DPAD_UP: vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
                DS4_DPAD_DOWN: vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
                DS4_DPAD_LEFT: vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
                DS4_DPAD_RIGHT: vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
            }
        elif self.controller_type == "ds4":
            self.gamepad = vg.VDS4Gamepad()
            self.is_xbox = False
            self._button_map = {
                DS4_BUTTON_CROSS: vg.DS4_BUTTONS.DS4_BUTTON_CROSS,
                DS4_BUTTON_CIRCLE: vg.DS4_BUTTONS.DS4_BUTTON_CIRCLE,
                DS4_BUTTON_SQUARE: vg.DS4_BUTTONS.DS4_BUTTON_SQUARE,
                DS4_BUTTON_TRIANGLE: vg.DS4_BUTTONS.DS4_BUTTON_TRIANGLE,
                DS4_BUTTON_L1: vg.DS4_BUTTONS.DS4_BUTTON_SHOULDER_LEFT,
                DS4_BUTTON_R1: vg.DS4_BUTTONS.DS4_BUTTON_SHOULDER_RIGHT,
                DS4_BUTTON_L3: vg.DS4_BUTTONS.DS4_BUTTON_THUMB_LEFT,
                DS4_BUTTON_R3: vg.DS4_BUTTONS.DS4_BUTTON_THUMB_RIGHT,
                DS4_BUTTON_OPTIONS: vg.DS4_BUTTONS.DS4_BUTTON_OPTIONS,
                DS4_BUTTON_SHARE: vg.DS4_BUTTONS.DS4_BUTTON_SHARE,
                DS4_BUTTON_PS: vg.DS4_SPECIAL_BUTTONS.DS4_SPECIAL_BUTTON_PS,
                DS4_BUTTON_TOUCHPAD: vg.DS4_SPECIAL_BUTTONS.DS4_SPECIAL_BUTTON_TOUCHPAD,
            }
            self._dpad_map = {
                DS4_DPAD_UP: vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NORTH,
                DS4_DPAD_DOWN: vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTH,
                DS4_DPAD_LEFT: vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_WEST,
                DS4_DPAD_RIGHT: vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_EAST,
                DS4_DPAD_NONE: vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NONE,
            }
        else:
            raise ValueError("Unsupported controller type. Use 'xbox360' or 'ds4'")

        # Add button release timers for optimized performance
        self._button_release_timers = {}
        self._pending_updates = False
        
        self._initialize_controller()
        self.update() # Send initial state

    def _initialize_controller(self):
        """Initializes the controller with a button press to wake it up."""
        print("Initializing controller...")
        if self.is_xbox:
            self.press_button_raw(self._button_map[XBOX_BUTTON_A])
            self.update()
            time.sleep(0.1)
            self.release_button_raw(self._button_map[XBOX_BUTTON_A])
        else:
            self.press_button_raw(self._button_map[DS4_BUTTON_CROSS])
            self.update()
            time.sleep(0.1)
            self.release_button_raw(self._button_map[DS4_BUTTON_CROSS])
        self.update()
        print("Controller initialized successfully!")

    def press_button_raw(self, button_code):
        """Presses a button using its raw vgamepad code."""
        self.gamepad.press_button(button=button_code)
        self._pending_updates = True

    def release_button_raw(self, button_code):
        """Releases a button using its raw vgamepad code."""
        self.gamepad.release_button(button=button_code)
        self._pending_updates = True

    def press_button(self, button_name: str):
        """Presses a button by its common name."""
        if button_name in self._button_map:
            self.press_button_raw(self._button_map[button_name])
        elif self.is_xbox and button_name in self._dpad_map: # Xbox D-pad are buttons
            self.press_button_raw(self._dpad_map[button_name])
        else:
            print(f"Warning: Button '{button_name}' not directly mapped for {self.controller_type} or is a special D-pad.")

    def release_button(self, button_name: str):
        """Releases a button by its common name."""
        if button_name in self._button_map:
            self.release_button_raw(self._button_map[button_name])
        elif self.is_xbox and button_name in self._dpad_map: # Xbox D-pad are buttons
            self.release_button_raw(self._dpad_map[button_name])
        else:
            print(f"Warning: Button '{button_name}' not directly mapped for {self.controller_type} or is a special D-pad.")

    def press_and_release(self, button_name: str, duration: float = 0.2, update_instantly: bool = True):
        """Presses and schedules release of a button without blocking.
        
        Args:
            button_name: Button name to press
            duration: Time in seconds before button is released
            update_instantly: Whether to send an update immediately
        """
        # Cancel any existing timer for this button
        if button_name in self._button_release_timers:
            self._button_release_timers[button_name].cancel()
            
        # Press the button
        self.press_button(button_name)
        
        # Create release timer
        timer = threading.Timer(duration, self._scheduled_release, args=[button_name])
        timer.daemon = True  # Don't block program exit
        self._button_release_timers[button_name] = timer
        timer.start()
        
        # Update if requested
        if update_instantly:
            self.update()
    
    def _scheduled_release(self, button_name: str):
        """Internal method for release timer callbacks"""
        self.release_button(button_name)
        print(f"Released button: {button_name}")
        self.update()
        if button_name in self._button_release_timers:
            del self._button_release_timers[button_name]

    def dpad(self, direction_name: str):
        """Sets D-pad direction for DS4, or presses/releases D-pad button for Xbox."""
        if self.is_xbox:
            if direction_name in self._dpad_map:
                # For Xbox, D-pad inputs are individual buttons.
                # This method will press and then expect a release or another dpad call to change.
                # To emulate DS4's directional_pad behavior, one would need to manage releases.
                # For simplicity here, we assume short presses or external release logic.
                print(f"Pressing Xbox D-Pad: {direction_name}")
                self.press_button_raw(self._dpad_map[direction_name])
                # Note: Xbox dpad buttons typically need explicit release.
                # Consider adding release logic or making it explicit like press_button/release_button
            else:
                print(f"Warning: D-pad direction '{direction_name}' not mapped for Xbox.")
        else: # DS4
            if direction_name in self._dpad_map:
                self.gamepad.directional_pad(direction=self._dpad_map[direction_name])
                self._pending_updates = True
            else:
                print(f"Warning: D-pad direction '{direction_name}' not mapped for DS4.")

    def dpad_pulse(self, direction_name: str, duration: float = 0.2, update_instantly: bool = True):
        """Pulses a D-pad direction without blocking.
        
        Args:
            direction_name: D-pad direction to press
            duration: Time in seconds before direction is released
            update_instantly: Whether to send an update immediately
        """
        if self.is_xbox:
            # For Xbox, use press_and_release with the appropriate D-pad button
            if direction_name in self._dpad_map:
                dpad_button = XBOX_BUTTON_DPAD_UP if direction_name == DS4_DPAD_UP else \
                              XBOX_BUTTON_DPAD_DOWN if direction_name == DS4_DPAD_DOWN else \
                              XBOX_BUTTON_DPAD_LEFT if direction_name == DS4_DPAD_LEFT else \
                              XBOX_BUTTON_DPAD_RIGHT
                self.press_and_release(dpad_button, duration, update_instantly)
        else:
            # For DS4, use the directional pad feature
            if direction_name in self._dpad_map:
                self.dpad(direction_name)
                
                # Schedule release
                def release_dpad():
                    self.dpad(DS4_DPAD_NONE)
                    self.update()
                
                timer = threading.Timer(duration, release_dpad)
                timer.daemon = True
                timer.start()
                
                if update_instantly:
                    self.update()

    def dpad_up(self):
        self.dpad(DS4_DPAD_UP) # DS4_DPAD_UP is generic key, maps to XBOX_BUTTON_DPAD_UP too

    def dpad_down(self):
        self.dpad(DS4_DPAD_DOWN)

    def dpad_left(self):
        self.dpad(DS4_DPAD_LEFT)

    def dpad_right(self):
        self.dpad(DS4_DPAD_RIGHT)
        
    def dpad_release(self): # Specifically for DS4 to reset dpad
        if not self.is_xbox:
            self.gamepad.directional_pad(direction=self._dpad_map[DS4_DPAD_NONE])
            self._pending_updates = True
        # For Xbox, individual D-pad buttons would need to be released e.g. release_button(XBOX_BUTTON_DPAD_LEFT)

    def left_joystick(self, x_value_float: float, y_value_float: float):
        """Sets the left joystick position. Values from -1.0 to 1.0."""
        self.gamepad.left_joystick_float(x_value_float=x_value_float, y_value_float=y_value_float)
        self._pending_updates = True

    def right_joystick(self, x_value_float: float, y_value_float: float):
        """Sets the right joystick position. Values from -1.0 to 1.0."""
        self.gamepad.right_joystick_float(x_value_float=x_value_float, y_value_float=y_value_float)
        self._pending_updates = True

    def joystick_pulse(self, is_left: bool, x_value: float, y_value: float, 
                      duration: float = 0.2, update_instantly: bool = True):
        """Moves a joystick and returns it to neutral position without blocking.
        
        Args:
            is_left: True for left stick, False for right stick
            x_value: X-axis value (-1.0 to 1.0)
            y_value: Y-axis value (-1.0 to 1.0)
            duration: Time in seconds before stick returns to neutral
            update_instantly: Whether to send an update immediately
        """
        # Move the stick
        if is_left:
            self.left_joystick(x_value, y_value)
        else:
            self.right_joystick(x_value, y_value)
            
        # Schedule return to neutral
        def reset_stick():
            if is_left:
                self.left_joystick(0.0, 0.0)
            else:
                self.right_joystick(0.0, 0.0)
            self.update()
            
        timer = threading.Timer(duration, reset_stick)
        timer.daemon = True
        timer.start()
        
        # Update if requested
        if update_instantly:
            self.update()

    def left_trigger_float(self, value_float: float):
        """Sets the left trigger value. Value from 0.0 to 1.0."""
        self.gamepad.left_trigger_float(value_float=value_float)
        self._pending_updates = True

    def right_trigger_float(self, value_float: float):
        """Sets the right trigger value. Value from 0.0 to 1.0."""
        self.gamepad.right_trigger_float(value_float=value_float)
        self._pending_updates = True

    def trigger_pulse(self, is_left: bool, value: float, 
                     duration: float = 0.2, update_instantly: bool = True):
        """Applies trigger pressure and releases it without blocking.
        
        Args:
            is_left: True for left trigger, False for right trigger
            value: Pressure value (0.0 to 1.0)
            duration: Time in seconds before trigger is released
            update_instantly: Whether to send an update immediately
        """
        # Press the trigger
        if is_left:
            self.left_trigger_float(value)
        else:
            self.right_trigger_float(value)
            
        # Schedule release
        def release_trigger():
            if is_left:
                self.left_trigger_float(0.0)
            else:
                self.right_trigger_float(0.0)
            self.update()
            
        timer = threading.Timer(duration, release_trigger)
        timer.daemon = True
        timer.start()
        
        # Update if requested
        if update_instantly:
            self.update()

    def update(self):
        """Sends all pending changes to the virtual gamepad."""
        self.gamepad.update()
        self._pending_updates = False

    def update_if_needed(self):
        """Sends updates only if there are pending changes."""
        if self._pending_updates:
            self.update()

    def reset(self):
        """Resets all controls to their default state."""
        # Cancel any pending release timers
        for timer in self._button_release_timers.values():
            timer.cancel()
        self._button_release_timers.clear()
        
        self.gamepad.reset()
        if not self.is_xbox: # DS4 needs explicit D-pad reset
            self.dpad_release()
        self.update()


class ControllerTester:
    """Test utility for verifying virtual controller inputs with games"""
    
    def __init__(self, controller_type="xbox360"):
        """Initialize the controller tester
        
        Args:
            controller_type: Type of controller to emulate ("xbox360" or "ds4")
        """
        self.controller = Controller(controller_type)
        self.is_xbox = self.controller.is_xbox # For convenience
        
        # Set up state variables
        self.running = False
        
    # Removed _initialize_controller as Controller handles it

    def press_dpad_up(self):
        """Press the D-pad up button"""
        print("Pressing D-pad UP")
        if self.is_xbox:
            self.controller.press_and_release(XBOX_BUTTON_DPAD_UP)
        else:
            self.controller.dpad_pulse(DS4_DPAD_UP)

    def press_dpad_down(self):
        """Press the D-pad down button"""
        print("Pressing D-pad DOWN")
        if self.is_xbox:
            self.controller.press_and_release(XBOX_BUTTON_DPAD_DOWN)
        else:
            self.controller.dpad_pulse(DS4_DPAD_DOWN)
            
    def press_dpad_left(self):
        """Press the D-pad left button"""
        print("Pressing D-pad LEFT")
        if self.is_xbox:
            self.controller.press_and_release(XBOX_BUTTON_DPAD_LEFT)
        else:
            self.controller.dpad_pulse(DS4_DPAD_LEFT)
            
    def press_dpad_right(self):
        """Press the D-pad right button"""
        print("Pressing D-pad RIGHT")
        if self.is_xbox:
            self.controller.press_and_release(XBOX_BUTTON_DPAD_RIGHT)
        else:
            self.controller.dpad_pulse(DS4_DPAD_RIGHT)
            
    def press_button_a_or_cross(self): # Renamed for clarity
        """Press the A (Xbox) or Cross (DS4) button"""
        print("Pressing A/Cross button")
        button_to_press = XBOX_BUTTON_A if self.is_xbox else DS4_BUTTON_CROSS
        self.controller.press_and_release(button_to_press)
            
    def analog_left_stick(self, x_value=-0.7, y_value=0.0):
        """Move the left analog stick"""
        direction = "LEFT" if x_value < 0 else "RIGHT" if x_value > 0 else "NEUTRAL X"
        direction_y = "UP" if y_value > 0 else "DOWN" if y_value < 0 else "NEUTRAL Y"
        print(f"Moving left stick {direction} / {direction_y}")
        self.controller.joystick_pulse(True, x_value, y_value)
        
    def analog_right_stick(self, x_value=0.7, y_value=0.0):
        """Move the right analog stick"""
        direction = "LEFT" if x_value < 0 else "RIGHT" if x_value > 0 else "NEUTRAL X"
        direction_y = "UP" if y_value > 0 else "DOWN" if y_value < 0 else "NEUTRAL Y"
        print(f"Moving right stick {direction} / {direction_y}")
        self.controller.joystick_pulse(False, x_value, y_value)
        
    def left_stick_delayed_up(self):
        """Move the left stick up for 5 seconds after a 1-second delay"""
        print("Left stick will move UP after 1 second delay (for 5 seconds)...")
        
        def delayed_up_thread():
            # Wait 1 second
            time.sleep(1.0)
            # Then move up for 5 seconds
            print("Moving left stick UP")
            self.controller.left_joystick(x_value_float=0.0, y_value_float=0.8)
            self.controller.update()
            time.sleep(5.0)
            # Reset position
            self.controller.left_joystick(x_value_float=0.0, y_value_float=0.0)
            self.controller.update()
            print("Left stick movement completed")
            
        threading.Thread(target=delayed_up_thread).start()
        
    def start_left_right_sequence(self):
        """Start a sequence that alternates between left and right inputs"""
        print("Starting LEFT-RIGHT D-pad sequence (10 times)...")
        
        def sequence_thread():
            count = 0
            while self.running and count < 10:
                if count % 2 == 0:
                    self.press_dpad_left()
                else:
                    self.press_dpad_right()
                time.sleep(1.0)
                count += 1
            self.running = False
            print("Sequence completed")
            
        self.running = True
        threading.Thread(target=sequence_thread).start()
        
    def start_left_right_analog_sequence(self):
        """Start a sequence that alternates between left and right analog inputs"""
        print("Starting LEFT-RIGHT analog stick sequence (10 times)...")
        
        def sequence_thread():
            count = 0
            while self.running and count < 10:
                if count % 2 == 0:
                    self.analog_left_stick(x_value=-0.7)
                else:
                    self.analog_left_stick(x_value=0.7)
                time.sleep(1.0)
                count += 1
            self.running = False
            print("Sequence completed")
            
        self.running = True
        threading.Thread(target=sequence_thread).start()
        
    def stop_sequence(self):
        """Stop any running sequence"""
        if self.running:
            print("Stopping sequence...")
            self.running = False
        else:
            print("No sequence running")


def run_console_test(controller_type="xbox360"):
    """Run a console-based test for controller inputs"""
    print("\n=== VIRTUAL CONTROLLER CONSOLE TEST ===")
    print(f"Controller type: {controller_type}")
    print("\nInstructions:")
    print("1. Launch your game")
    print("2. Make sure controller input is enabled in the game")
    print("3. Use the following options to test if the game responds to controller inputs\n")
    
    try:
        tester = ControllerTester(controller_type)
        
        while True:
            print("\nTest Options:")
            print("1. Press D-pad Left")
            print("2. Press D-pad Right")
            print("3. Press A/Cross Button")
            print("4. Move Left Stick Left")
            print("5. Move Left Stick Right")
            print("6. Start Left-Right D-pad Sequence")
            print("7. Start Left-Right Analog Sequence")
            print("8. Stop Sequence")
            print("9. Press D-pad Up")
            print("10. Press D-pad Down")
            print("11. Exit Test")
            
            choice = input("\nEnter your choice (1-11): ")
            
            if choice == '1':
                tester.press_dpad_left()
            elif choice == '2':
                tester.press_dpad_right()
            elif choice == '3':
                tester.press_button_a_or_cross() # Updated method name
            elif choice == '4':
                tester.analog_left_stick(x_value=-0.7)
            elif choice == '5':
                tester.analog_left_stick(x_value=0.7)
            elif choice == '6':
                tester.start_left_right_sequence()
            elif choice == '7':
                tester.start_left_right_analog_sequence()
            elif choice == '8':
                tester.stop_sequence()
            elif choice == '9':
                tester.press_dpad_up() # New option
            elif choice == '10':
                tester.press_dpad_down() # New option
            elif choice == '11':
                print("Exiting controller test...")
                break
            else:
                print("Invalid choice. Please try again.")
    
    except Exception as e:
        print(f"Error in controller test: {e}")
        return

def run_gui_test(controller_type="xbox360"):
    """Run a GUI-based test for controller inputs"""
    try:
        import tkinter as tk
        from tkinter import ttk
        
        tester = ControllerTester(controller_type)
        
        root = tk.Tk()
        root.title("Controller Test")
        root.geometry("400x400")
        
        # Controller type indicator
        controller_type_str = "Xbox 360" if tester.is_xbox else "DualShock 4"
        ttk.Label(root, text=f"Testing {controller_type_str} Controller", font=("Arial", 14)).pack(pady=10)
        
        # Instructions
        ttk.Label(root, text="1. Launch your game", font=("Arial", 10)).pack(anchor="w", padx=20)
        ttk.Label(root, text="2. Make sure controller input is enabled", font=("Arial", 10)).pack(anchor="w", padx=20)
        ttk.Label(root, text="3. Press buttons below to test", font=("Arial", 10)).pack(anchor="w", padx=20)
        
        # Individual button tests
        button_frame = ttk.Frame(root)
        button_frame.pack(pady=20, fill="x")
        
        ttk.Button(button_frame, text="D-Pad Left", command=tester.press_dpad_left).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(button_frame, text="D-Pad Right", command=tester.press_dpad_right).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(button_frame, text="A/Cross Button", command=tester.press_button_a_or_cross).grid(row=0, column=2, padx=5, pady=5) # Updated command
        ttk.Button(button_frame, text="D-Pad Up", command=tester.press_dpad_up).grid(row=0, column=3, padx=5, pady=5) # New button
        ttk.Button(button_frame, text="D-Pad Down", command=tester.press_dpad_down).grid(row=0, column=4, padx=5, pady=5) # New button
        
        ttk.Button(button_frame, text="Left Stick Left", 
                  command=lambda: tester.analog_left_stick(x_value=-0.7)).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(button_frame, text="Left Stick Right", 
                  command=lambda: tester.analog_left_stick(x_value=0.7)).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(button_frame, text="Right Stick Right", 
                  command=lambda: tester.analog_right_stick(x_value=0.7)).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(button_frame, text="Left Stick Delayed Up", 
                  command=tester.left_stick_delayed_up).grid(row=1, column=3, padx=5, pady=5)
        
        # Sequence tests
        sequence_frame = ttk.LabelFrame(root, text="Automated Tests")
        sequence_frame.pack(pady=10, fill="x", padx=20)
        
        ttk.Button(sequence_frame, text="Start Left-Right D-Pad Sequence", 
                  command=tester.start_left_right_sequence).pack(fill="x", padx=5, pady=5)
        ttk.Button(sequence_frame, text="Start Left-Right Analog Sequence", 
                  command=tester.start_left_right_analog_sequence).pack(fill="x", padx=5, pady=5)
        ttk.Button(sequence_frame, text="Stop Sequence", 
                  command=tester.stop_sequence).pack(fill="x", padx=5, pady=5)
        
        # Status indicator
        status_label = ttk.Label(root, text="Ready to test", font=("Arial", 10))
        status_label.pack(pady=10)
        
        # Start UI
        root.mainloop()
        
    except ImportError:
        print("GUI libraries not available. Running console version instead.")
        run_console_test(controller_type)
    except Exception as e:
        print(f"Error starting GUI: {e}")
        print("Falling back to console version...")
        run_console_test(controller_type)

def main():
    """Main function to run the controller test"""
    print("Starting controller test")
    print("Make sure you have vgamepad installed (pip install vgamepad)")
    print("Make sure ViGEmBus driver is installed (automatically installed with vgamepad)")
    
    controller_type = input("Choose controller type (xbox360/ds4) [default: xbox360]: ").strip()
    if not controller_type:
        controller_type = "xbox360"
    
    # Determine if we should try to use GUI or just go with console
    use_gui = input("Use GUI interface? (y/n) [default: y]: ").strip().lower()
    if not use_gui or use_gui.startswith('y'):
        try:
            run_gui_test(controller_type)
        except Exception as e:
            print(f"Error initializing GUI: {e}")
            print("Falling back to console version...")
            run_console_test(controller_type)
    else:
        run_console_test(controller_type)

if __name__ == "__main__":
    main()
