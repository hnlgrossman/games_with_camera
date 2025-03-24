import sys
import time

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

def send_key_event_win32(key, press_type):
    """
    Send key events using win32api - approach that works for game compatibility
    """
    if press_type == "down":
        win32api.keybd_event(key, win32api.MapVirtualKey(key, 0), 0, 0)
    elif press_type == "up":
        win32api.keybd_event(key, win32api.MapVirtualKey(key, 0), KEYEVENTF_KEYUP, 0)

def press_and_release(key):
    """Press and release a key using win32api"""
    send_key_event_win32(key, "down")
    import time
    time.sleep(0.05)  # Small delay between press and release
    send_key_event_win32(key, "up")

def trigger_up():
    """Trigger UP arrow key press"""
    press_and_release(VK_UP)

def trigger_down():
    """Trigger DOWN arrow key press"""
    press_and_release(VK_DOWN)

def trigger_left():
    """Trigger LEFT arrow key press"""
    press_and_release(VK_LEFT)

def trigger_right():
    """Trigger RIGHT arrow key press"""
    press_and_release(VK_RIGHT)

# Example usage
if __name__ == "__main__":
    # time.sleep(6)
    trigger_up()
    # print("Arrow key functions loaded. Import and use the trigger_* functions.")
    # print("Example: trigger_up(), trigger_down(), trigger_left(), trigger_right()")