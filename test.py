import time
import sys
import random

try:
    import win32api
except ImportError:
    print("Required package not found. Installing pywin32...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pywin32"])
    print("Please restart the script now.")
    sys.exit(1)

# Define key codes for all arrow keys
VK_UP = 0x26     # UP arrow
VK_DOWN = 0x28   # DOWN arrow
VK_LEFT = 0x25   # LEFT arrow
VK_RIGHT = 0x27  # RIGHT arrow
KEYEVENTF_KEYUP = 0x0002

# Create a mapping of keys for easy reference
key_names = {
    VK_UP: "UP",
    VK_DOWN: "DOWN",
    VK_LEFT: "LEFT",
    VK_RIGHT: "RIGHT"
}

def send_key_event_win32(key, press_type):
    """
    Send key events using win32api - approach that works for game compatibility
    """
    if press_type == "down":
        win32api.keybd_event(key, win32api.MapVirtualKey(key, 0), 0, 0)
    elif press_type == "up":
        win32api.keybd_event(key, win32api.MapVirtualKey(key, 0), KEYEVENTF_KEYUP, 0)

def press_and_release_win32(key):
    """Press and release a key using win32api"""
    send_key_event_win32(key, "down")
    time.sleep(0.05)  # Small delay between press and release
    send_key_event_win32(key, "up")

def test_specific_key(key):
    """Test a specific arrow key"""
    print(f"Pressing {key_names[key]} key")
    press_and_release_win32(key)

def main():
    print("\n=== ARROW KEYS TESTER FOR GAMES ===")
    print("This script uses win32api to send arrow key inputs to games")
    print("\nOptions:")
    print("1. Test UP key")
    print("2. Test DOWN key")
    print("3. Test LEFT key")
    print("4. Test RIGHT key")
    print("5. Test all keys in sequence")
    print("6. Test random keys")
    print("7. Continuous mode (one key repeatedly)")
    print("8. Exit")
    
    choice = input("\nEnter your choice (1-8): ")
    
    if choice == "1":
        test_key_repeatedly(VK_UP)
    elif choice == "2":
        test_key_repeatedly(VK_DOWN)
    elif choice == "3":
        test_key_repeatedly(VK_LEFT)
    elif choice == "4":
        test_key_repeatedly(VK_RIGHT)
    elif choice == "5":
        test_keys_in_sequence()
    elif choice == "6":
        test_random_keys()
    elif choice == "7":
        continuous_mode()
    elif choice == "8":
        print("Exiting...")
        sys.exit(0)
    else:
        print("Invalid choice. Please try again.")
        main()

def test_key_repeatedly(key):
    """Test a specific key repeatedly"""
    print(f"\nStarting in 5 seconds. Will press {key_names[key]} key every second.")
    print("Press Ctrl+C to stop.")
    time.sleep(5)
    
    try:
        while True:
            test_specific_key(key)
            time.sleep(0.95)  # Total ~1 second including the 0.05s delay
    except KeyboardInterrupt:
        print("\nStopped by user")
        main()

def test_keys_in_sequence():
    """Test all arrow keys in sequence"""
    print("\nStarting in 5 seconds. Will press all arrow keys in sequence.")
    print("Press Ctrl+C to stop.")
    time.sleep(5)
    
    keys = [VK_UP, VK_RIGHT, VK_DOWN, VK_LEFT]
    try:
        while True:
            for key in keys:
                test_specific_key(key)
                time.sleep(0.95)
    except KeyboardInterrupt:
        print("\nStopped by user")
        main()

def test_random_keys():
    """Test random arrow keys"""
    print("\nStarting in 5 seconds. Will press random arrow keys.")
    print("Press Ctrl+C to stop.")
    time.sleep(5)
    
    keys = [VK_UP, VK_RIGHT, VK_DOWN, VK_LEFT]
    try:
        while True:
            key = random.choice(keys)
            test_specific_key(key)
            time.sleep(0.95)
    except KeyboardInterrupt:
        print("\nStopped by user")
        main()

def continuous_mode():
    """Continuous mode menu"""
    print("\nContinuous Mode - Choose a key to press repeatedly:")
    print("1. UP key")
    print("2. DOWN key")
    print("3. LEFT key")
    print("4. RIGHT key")
    print("5. Go back")
    
    choice = input("\nEnter your choice (1-5): ")
    
    if choice == "1":
        interval = get_interval()
        continuous_key_press(VK_UP, interval)
    elif choice == "2":
        interval = get_interval()
        continuous_key_press(VK_DOWN, interval)
    elif choice == "3":
        interval = get_interval()
        continuous_key_press(VK_LEFT, interval)
    elif choice == "4":
        interval = get_interval()
        continuous_key_press(VK_RIGHT, interval)
    elif choice == "5":
        main()
    else:
        print("Invalid choice.")
        continuous_mode()

def get_interval():
    """Get interval time from user"""
    try:
        interval = float(input("\nEnter interval between keypresses (seconds, e.g. 0.5): "))
        if interval <= 0:
            print("Interval must be positive. Using default of 1 second.")
            return 1.0
        return interval
    except ValueError:
        print("Invalid input. Using default of 1 second.")
        return 1.0

def continuous_key_press(key, interval):
    """Press a key continuously with custom interval"""
    print(f"\nStarting in 5 seconds. Will press {key_names[key]} key every {interval} seconds.")
    print("Press Ctrl+C to stop.")
    time.sleep(5)
    
    try:
        while True:
            test_specific_key(key)
            time.sleep(interval - 0.05 if interval > 0.05 else 0)
    except KeyboardInterrupt:
        print("\nStopped by user")
        main()

if __name__ == "__main__":
    main()