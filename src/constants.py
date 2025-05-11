import mediapipe as mp

# Landmark indices for common body parts
LEFT_FOOT_INDEX = 32
RIGHT_FOOT_INDEX = 31
NOSE_INDEX = mp.solutions.pose.PoseLandmark.NOSE
LEFT_KNEE_INDEX = mp.solutions.pose.PoseLandmark.LEFT_KNEE
RIGHT_KNEE_INDEX = mp.solutions.pose.PoseLandmark.RIGHT_KNEE
LEFT_SHOULDER_INDEX = mp.solutions.pose.PoseLandmark.LEFT_SHOULDER
RIGHT_SHOULDER_INDEX = mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER
LEFT_HIP_INDEX = mp.solutions.pose.PoseLandmark.LEFT_HIP
RIGHT_HIP_INDEX = mp.solutions.pose.PoseLandmark.RIGHT_HIP


# Coordinate indices
X_COORDINATE_INDEX = 0
Y_COORDINATE_INDEX = 1
Z_COORDINATE_INDEX = 2 


# events
STEP_RIGHT="step_right"
STEP_LEFT="step_left"
JUMP="jump"
BEND="bend"