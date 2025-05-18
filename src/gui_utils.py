import cv2
import numpy as np

def get_available_camera_indices(max_cameras_to_check=5):
    """
    Checks for available cameras and returns a list of their indices.
    Tries to open cameras by index 0, 1, 2,...
    """
    available_indices = []
    print("Detecting available cameras...")
    for i in range(max_cameras_to_check):
        # Try to open with default API, then MSMF if available (for Windows)
        cap = cv2.VideoCapture(i)
        if not cap.isOpened():
             cap = cv2.VideoCapture(i + cv2.CAP_MSMF) # Try with MSMF backend on Windows

        if cap.isOpened():
            available_indices.append(i)
            cap.release()
        # Unlike before, we don't break early to find potentially non-contiguous cameras
        # (e.g. index 0 and 2 might be available, but not 1)
    
    if not available_indices:
        print("No cameras found.")
    else:
        print(f"Available camera indices: {available_indices}")
    return available_indices

def welcome_screen():
    """
    Displays a welcome screen allowing the user to select a camera and toggle sound.
    The user can cycle through available camera previews.

    Returns:
        tuple: (selected_camera_index, sound_enabled) or (None, None) if quit or no cameras.
    """
    camera_indices = get_available_camera_indices()
    if not camera_indices:
        print("No cameras available to select from. Exiting.")
        # Attempt to close any stray OpenCV windows, just in case
        try:
            cv2.destroyAllWindows()
        except cv2.error: # Suppress error if no windows exist
            pass
        return None, None

    current_selection_idx = 0  # Index within the camera_indices list
    sound_enabled = True
    
    window_name = "Welcome - Camera & Sound Selection"
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

    # Store active camera capture objects to avoid reopening them constantly if possible,
    # or manage opening/releasing them carefully.
    active_cap = None 

    while True:
        selected_camera_device_index = camera_indices[current_selection_idx]

        # Open or switch camera
        if active_cap is None or active_cap.get(cv2.CAP_PROP_POS_FRAMES) == -1 or int(active_cap.get(cv2.CAP_PROP_BACKEND)) != selected_camera_device_index: # Check if wrong cap or closed
            if active_cap is not None:
                active_cap.release()
            
            active_cap = cv2.VideoCapture(selected_camera_device_index)
            if not active_cap.isOpened(): # Try with MSMF as fallback
                 active_cap = cv2.VideoCapture(selected_camera_device_index + cv2.CAP_MSMF)

            if not active_cap.isOpened():
                print(f"Error: Could not open camera {selected_camera_device_index}.")
                # Create a black frame with an error message
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(frame, f"Error opening cam {selected_camera_device_index}", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                # Set a smaller resolution for preview if possible, to improve performance
                active_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                active_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


        ret, frame = active_cap.read() if active_cap.isOpened() else (False, None)

        if not ret or frame is None:
            frame = np.zeros((480, 640, 3), dtype=np.uint8) # Blank frame on error/no signal
            cv2.putText(frame, f"Camera {selected_camera_device_index}: No signal or error", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            frame = cv2.flip(frame, 1) # Flip for a mirror view, common for self-view

        display_frame = frame.copy()
        height, width, _ = display_frame.shape
        
        # Overlay information text
        # Box for text background
        text_bg_height = 130
        cv2.rectangle(display_frame, (0, height - text_bg_height), (width, height), (0,0,0), -1)

        info_line1 = f"PREVIEW Camera: {selected_camera_device_index} ({current_selection_idx + 1}/{len(camera_indices)})"
        info_line2 = f"Sound: {'ON' if sound_enabled else 'OFF'}"
        
        controls_line1 = "Controls:"
        controls_line2 = "(N)ext Cam | (P)rev Cam"
        controls_line3 = "(S)elect This Camera"
        controls_line4 = "(T)oggle Sound | (ESC) Quit"

        text_color = (50, 205, 50) # Greenish
        shadow_color = (0,0,0)
        font_scale = 0.6
        thickness = 1

        # Function to draw text with a slight shadow for better readability
        def draw_text_with_shadow(img, text, pos, font, scale, color, shadow_color, thick):
            x, y = pos
            cv2.putText(img, text, (x+1, y+1), font, scale, shadow_color, thick, cv2.LINE_AA)
            cv2.putText(img, text, (x, y), font, scale, color, thick, cv2.LINE_AA)

        y_offset = height - text_bg_height + 20
        draw_text_with_shadow(display_frame, info_line1, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, shadow_color, thickness)
        y_offset += 20
        draw_text_with_shadow(display_frame, info_line2, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, shadow_color, thickness)
        y_offset += 25
        draw_text_with_shadow(display_frame, controls_line1, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, font_scale-0.1, (220,220,220), shadow_color, thickness)
        y_offset += 15
        draw_text_with_shadow(display_frame, controls_line2, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, font_scale-0.1, (220,220,220), shadow_color, thickness)
        y_offset += 15
        draw_text_with_shadow(display_frame, controls_line3, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, font_scale-0.1, (220,220,220), shadow_color, thickness)
        y_offset += 15
        draw_text_with_shadow(display_frame, controls_line4, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, font_scale-0.1, (220,220,220), shadow_color, thickness)

        cv2.imshow(window_name, display_frame)
        key = cv2.waitKey(30) & 0xFF # Use a small delay for live preview update

        if key == 27:  # ESC
            print("Selection cancelled by user.")
            selected_camera_device_index = None # Indicate cancellation
            # sound_enabled is not relevant if cancelled, but keep its state for clarity
            break
        elif key == ord('n'):
            current_selection_idx = (current_selection_idx + 1) % len(camera_indices)
            if active_cap: active_cap.release(); active_cap = None # Force reopen for next camera
        elif key == ord('p'):
            current_selection_idx = (current_selection_idx - 1 + len(camera_indices)) % len(camera_indices)
            if active_cap: active_cap.release(); active_cap = None # Force reopen for next camera
        elif key == ord('s'):
            print(f"Camera {selected_camera_device_index} selected. Sound: {'ON' if sound_enabled else 'OFF'}")
            break 
        elif key == ord('t'):
            sound_enabled = not sound_enabled
            print(f"Sound toggled to: {'ON' if sound_enabled else 'OFF'}")
    
    # Release the active camera capture, if any
    if active_cap is not None:
        active_cap.release()
    cv2.destroyAllWindows()
    
    if selected_camera_device_index is None: # User quit with ESC
        return None, None # Return None for camera_index to signal cancellation
    return selected_camera_device_index, sound_enabled

if __name__ == '__main__':
    # Test the welcome screen
    print("Testing welcome screen...")
    selected_cam, sound_on = welcome_screen()
    if selected_cam is not None:
        print(f"Returned from test: Camera Index = {selected_cam}, Sound Enabled = {sound_on}")
    else:
        print("Exited from test without selection or no cameras found.")
    print("Test finished. Press Enter to close this terminal.")
    input()