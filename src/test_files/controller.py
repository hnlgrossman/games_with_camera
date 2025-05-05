import vgamepad as vg
import time
import threading
import sys

class ControllerTester:
    """Test utility for verifying virtual controller inputs with games"""
    
    def __init__(self, controller_type="xbox360"):
        """Initialize the controller tester
        
        Args:
            controller_type: Type of controller to emulate ("xbox360" or "ds4")
        """
        # Create virtual controller
        if controller_type.lower() == "xbox360":
            self.gamepad = vg.VX360Gamepad()
            self.is_xbox = True
        elif controller_type.lower() == "ds4":
            self.gamepad = vg.VDS4Gamepad()
            self.is_xbox = False
        else:
            raise ValueError("Unsupported controller type. Use 'xbox360' or 'ds4'")
        
        # Wake up the controller
        self._initialize_controller()
        
        # Set up state variables
        self.running = False
        
    def _initialize_controller(self):
        """Initialize the controller with a button press to wake it up"""
        print("Initializing controller...")
        if self.is_xbox:
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
            self.gamepad.update()
            time.sleep(0.1)
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
            self.gamepad.update()
        else:
            self.gamepad.press_button(button=vg.DS4_BUTTONS.DS4_BUTTON_CROSS)
            self.gamepad.update()
            time.sleep(0.1)
            self.gamepad.release_button(button=vg.DS4_BUTTONS.DS4_BUTTON_CROSS)
            self.gamepad.update()
        print("Controller initialized successfully!")
    
    def press_dpad_left(self):
        """Press the D-pad left button"""
        print("Pressing D-pad LEFT")
        if self.is_xbox:
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
            self.gamepad.update()
            time.sleep(0.2)
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
            self.gamepad.update()
        else:
            self.gamepad.directional_pad(direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_WEST)
            self.gamepad.update()
            time.sleep(0.2)
            self.gamepad.directional_pad(direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NONE)
            self.gamepad.update()
            
    def press_dpad_right(self):
        """Press the D-pad right button"""
        print("Pressing D-pad RIGHT")
        if self.is_xbox:
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
            self.gamepad.update()
            time.sleep(0.2)
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
            self.gamepad.update()
        else:
            self.gamepad.directional_pad(direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_EAST)
            self.gamepad.update()
            time.sleep(0.2)
            self.gamepad.directional_pad(direction=vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NONE)
            self.gamepad.update()
            
    def press_button_a(self):
        """Press the A/Cross button"""
        print("Pressing A/Cross button")
        if self.is_xbox:
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
            self.gamepad.update()
            time.sleep(0.2)
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
            self.gamepad.update()
        else:
            self.gamepad.press_button(button=vg.DS4_BUTTONS.DS4_BUTTON_CROSS)
            self.gamepad.update()
            time.sleep(0.2)
            self.gamepad.release_button(button=vg.DS4_BUTTONS.DS4_BUTTON_CROSS)
            self.gamepad.update()
            
    def analog_left_stick(self, x_value=-0.7, y_value=0.0):
        """Move the left analog stick"""
        direction = "LEFT" if x_value < 0 else "RIGHT"
        print(f"Moving left stick {direction}")
        self.gamepad.left_joystick_float(x_value_float=x_value, y_value_float=y_value)
        self.gamepad.update()
        time.sleep(0.2)
        self.gamepad.left_joystick_float(x_value_float=0.0, y_value_float=0.0)
        self.gamepad.update()
        
    def analog_right_stick(self, x_value=0.7, y_value=0.0):
        """Move the right analog stick"""
        direction = "LEFT" if x_value < 0 else "RIGHT"
        print(f"Moving right stick {direction}")
        self.gamepad.right_joystick_float(x_value_float=x_value, y_value_float=y_value)
        self.gamepad.update()
        time.sleep(0.2)
        self.gamepad.right_joystick_float(x_value_float=0.0, y_value_float=0.0)
        self.gamepad.update()
        
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
            print("9. Exit Test")
            
            choice = input("\nEnter your choice (1-9): ")
            
            if choice == '1':
                tester.press_dpad_left()
            elif choice == '2':
                tester.press_dpad_right()
            elif choice == '3':
                tester.press_button_a()
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
        ttk.Button(button_frame, text="A/Cross Button", command=tester.press_button_a).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Left Stick Left", 
                  command=lambda: tester.analog_left_stick(x_value=-0.7)).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(button_frame, text="Left Stick Right", 
                  command=lambda: tester.analog_left_stick(x_value=0.7)).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(button_frame, text="Right Stick Right", 
                  command=lambda: tester.analog_right_stick(x_value=0.7)).grid(row=1, column=2, padx=5, pady=5)
        
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
