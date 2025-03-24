import cv2
import mediapipe as mp
import numpy as np
import time
import threading

class MovementDetector:
    def __init__(self):
        # Initialize MediaPipe Pose model
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Movement detection parameters
        self.prev_landmarks = None
        self.stable_position = None
        self.stable_counter = 0
        self.required_stable_frames = 15  # Reduced from 30 to make it easier to establish baseline
        
        # Jump detection
        self.jump_threshold = 0.025  # Lowered from 0.1 to make it more sensitive
        self.base_height = None
        
        # Step detection
        self.step_threshold = 0.05  # Lowered from 0.1 to make it more sensitive
        self.base_hip_x = None
        
        # Bend detection
        self.bend_threshold = -0.1  # Lowered from 0.2 to make it more sensitive
        self.base_hip_knee_angle = None
        
        # Movement cooldown to prevent multiple detections
        self.last_detection_time = 0
        self.cooldown_period = 1.0  # seconds
        
        # Debug flag
        self.debug = False
        self.debug_interval = 30  # Print debug info every 30 frames
        self.frame_counter = 0

        self.bend_check = None
        self.bend_lock = threading.Lock()
        self.bend_result = None
        self.bend_thread = None
        
    def start_camera(self):
        cap = cv2.VideoCapture(1)  # Try 0 first (default camera)
        
        if not cap.isOpened():
            print("Could not open camera with index 0, trying index 1...")
            cap = cv2.VideoCapture(1)  # Try index 1 if 0 fails
            
            if not cap.isOpened():
                print("Failed to open camera. Please check your camera connection.")
                return
                
        print("Camera opened successfully!")
        print("Please stand still to establish a baseline position...")
        
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Failed to read from camera")
                break
                
            # Flip image horizontally for a mirror effect
            image = cv2.flip(image, 1)
            
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Process the image and detect pose
            results = self.pose.process(rgb_image)
            
            # Draw the pose landmarks on the image
            if results.pose_landmarks:
                self.mp_drawing.draw_landmarks(
                    image, 
                    results.pose_landmarks, 
                    self.mp_pose.POSE_CONNECTIONS
                )
                
                # Detect movements
                movement = self.detect_movement(results.pose_landmarks)
                if movement:
                    print(f"Movement detected: {movement}")
                    # cv2.putText(image, movement, (50, 50), 
                    #             cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                if self.frame_counter % 30 == 0:  # Every 30 frames
                    print("No pose landmarks detected. Make sure your full body is visible.")
            
            # Display the image
            cv2.imshow('Movement Detection', image)
            
            # Exit on ESC
            if cv2.waitKey(5) & 0xFF == 27:
                break
                
            self.frame_counter += 1
                
        cap.release()
        cv2.destroyAllWindows()
        
    def detect_movement(self, landmarks):
        if landmarks is None:
            return None
            
        # Convert landmarks to numpy array for easier calculations
        landmark_points = np.array([[lm.x, lm.y, lm.z] for lm in landmarks.landmark])
        
        # Establish a stable reference position
        if self.stable_position is None:
            if self.prev_landmarks is None:
                self.prev_landmarks = landmark_points
                return None
            
            # Check if position is stable
            distance = np.linalg.norm(landmark_points - self.prev_landmarks)
            
            if self.debug and self.frame_counter % self.debug_interval == 0:
                print(f"Stability check: distance = {distance:.4f}, counter = {self.stable_counter}/{self.required_stable_frames}")
                
            if distance < 0.05:  # Increased from 0.02 to 0.05 to account for natural movement
                self.stable_counter += 1
                if self.debug and self.frame_counter % 10 == 0:  # Print more often during stability establishment
                    print(f"Standing still... {self.stable_counter}/{self.required_stable_frames}")
            else:
                if self.stable_counter > 0:
                    print("Movement detected, resetting stability counter")
                self.stable_counter = 0
            
            if self.stable_counter >= self.required_stable_frames:
                self.stable_position = landmark_points
                self.base_height = landmarks.landmark[self.mp_pose.PoseLandmark.NOSE].y
                self.base_hip_x = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_HIP].x
                # Calculate base hip-knee angle for bend detection
                self.base_hip_knee_angle = self._calculate_hip_knee_angle(landmarks)
                print("\n===============================================")
                print("REFERENCE POSITION ESTABLISHED - START MOVING!")
                print("===============================================\n")
                print(f"Base height (nose): {self.base_height:.4f}")
                print(f"Base hip x: {self.base_hip_x:.4f}")
                print(f"Base hip-knee angle: {self.base_hip_knee_angle:.4f}")
            
            self.prev_landmarks = landmark_points
            return None
        
        # Check cooldown period
        current_time = time.time()
        if current_time - self.last_detection_time < self.cooldown_period:
            return None
        
        # print(f"Frame counter: {self.frame_counter}")
        # Debug prints every N frames
        if self.debug and self.frame_counter % self.debug_interval == 0:
            # Detect jump
            nose_y = landmarks.landmark[self.mp_pose.PoseLandmark.NOSE].y
            jump_diff = self.base_height - nose_y
            
            # Detect step right and left
            left_hip_x = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_HIP].x
            step_right_diff = left_hip_x - self.base_hip_x
            step_left_diff = self.base_hip_x - left_hip_x
            
            # Detect bend
            current_hip_knee_angle = self._calculate_hip_knee_angle(landmarks)
            bend_diff = self.base_hip_knee_angle - current_hip_knee_angle
            
            print("\nDEBUG VALUES:")
            print(f"Jump: current={nose_y:.4f}, base={self.base_height:.4f}, diff={jump_diff:.4f}, threshold={self.jump_threshold:.4f}")
            print(f"Step Right: current={left_hip_x:.4f}, base={self.base_hip_x:.4f}, diff={step_right_diff:.4f}, threshold={self.step_threshold:.4f}")
            print(f"Step Left: current={left_hip_x:.4f}, base={self.base_hip_x:.4f}, diff={step_left_diff:.4f}, threshold={self.step_threshold:.4f}")
            print(f"Bend: current={current_hip_knee_angle:.4f}, base={self.base_hip_knee_angle:.4f}, diff={bend_diff:.4f}, threshold={self.bend_threshold:.4f}")
        
        # Detect jump
        nose_y = landmarks.landmark[self.mp_pose.PoseLandmark.NOSE].y
        jump_diff = self.base_height - nose_y
        if jump_diff > self.jump_threshold:
            self.last_detection_time = current_time
            return "Jump"
        
        # Detect step right and left
        left_hip_x = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_HIP].x
        step_right_diff = left_hip_x - self.base_hip_x
        if step_right_diff > self.step_threshold:
            self.last_detection_time = current_time
            return "Step Right"
            
        step_left_diff = self.base_hip_x - left_hip_x
        if step_left_diff > self.step_threshold:
            self.last_detection_time = current_time
            return "Step Left"
        
        # Check if we have a bend result from the async thread
        if self.bend_result:
            result = self.bend_result
            self.bend_result = None
            return result
            
        # Start async bend detection if not already running
        if self.bend_thread is None or not self.bend_thread.is_alive():
            # Make a copy of the landmarks to pass to the thread
            landmarks_copy = landmarks
            self.bend_thread = threading.Thread(
                target=self._process_bend_detection,
                args=(landmarks_copy, current_time)
            )
            self.bend_thread.daemon = True
            self.bend_thread.start()
                    
        return None
    
    def _process_bend_detection(self, landmarks, current_time):
        """Process bend detection in a separate thread"""
        # Calculate hip-knee angle
        current_hip_knee_angle = self._calculate_hip_knee_angle(landmarks)
        bend_diff = self.base_hip_knee_angle - current_hip_knee_angle
        is_bend = bend_diff < self.bend_threshold
        
        with self.bend_lock:
            if is_bend:
                # print(f"Bend detected: {current_time}")
                # print(f"Bend check: {self.bend_check}")
                
                if self.bend_check is None:
                    self.bend_check = [current_time]
                elif len(self.bend_check):
                    if len(self.bend_check) == 1:
                        self.bend_check.append(current_time)
                    if self.bend_check[1] - self.bend_check[0] > 1:
                        self.bend_check = None
                        self.last_detection_time = current_time
                        self.bend_result = "Bend"
                    else:
                        self.bend_check[1] = current_time
            else:
                self.bend_check = None
    
    def _calculate_hip_knee_angle(self, landmarks):
        # Get relevant landmarks
        hip = np.array([
            landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_HIP].x,
            landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_HIP].y
        ])
        knee = np.array([
            landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_KNEE].x,
            landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_KNEE].y
        ])
        ankle = np.array([
            landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_ANKLE].x,
            landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_ANKLE].y
        ])
        
        # Calculate vectors
        hip_to_knee = knee - hip
        knee_to_ankle = ankle - knee
        
        # Calculate angle
        dot_product = np.dot(hip_to_knee, knee_to_ankle)
        norm_product = np.linalg.norm(hip_to_knee) * np.linalg.norm(knee_to_ankle)
        
        # Avoid division by zero or numerical instability
        if norm_product < 1e-10:
            return 0
            
        # Clamp value to avoid invalid input to arccos
        cos_angle = max(min(dot_product / norm_product, 1.0), -1.0)
        angle = np.arccos(cos_angle)
        
        return angle

if __name__ == "__main__":
    detector = MovementDetector()
    detector.start_camera() 