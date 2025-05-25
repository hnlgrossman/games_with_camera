from typing import Optional, Tuple, List

from ..constants import START_LEFT, START_RIGHT, END_LEFT, END_RIGHT
from src.constants import LEFT_WRIST_INDEX, RIGHT_WRIST_INDEX, Y_COORDINATE_INDEX
from .base_movement import BaseMovement


class AsideMovement(BaseMovement):
    """Detects step movements (left or right)."""

    STATE_IDLE = "IDLE"
    STATE_ACTIVE_RIGHT = "ACTIVE_RIGHT"
    STATE_ACTIVE_LEFT = "ACTIVE_LEFT"

    def __init__(self, analyzer: 'MovementAnalyzer', debug: bool = False):
        super().__init__(analyzer, debug)
        self.START_THRESHOLD = 0.05
        self.END_THRESHOLD = 0.05  # User: "when the handes y diff is less then 0.5"
        self.current_motion_state: str = self.STATE_IDLE
        # print(f"AsideMovement.__init__: initialized - start_thresh: {self.START_THRESHOLD}, end_thresh: {self.END_THRESHOLD}, initial_state: {self.current_motion_state}")

    @property
    def detectable_moves(self) -> List[str]:
        """Returns the list of movement types this detector can detect."""
        return [START_RIGHT, START_LEFT, END_RIGHT, END_LEFT]
        
    
    def detect(self) -> Optional[str]:
        landmarks = self.analyzer.current_landmark_points
        if landmarks is None:
            # print("AsideMovement.detect: info - landmarks are None, no analysis possible.") # Adhering to no comment policy
            return None

        try:
            left_wrist_coords = landmarks[LEFT_WRIST_INDEX]
            right_wrist_coords = landmarks[RIGHT_WRIST_INDEX]
        except IndexError:
            # print(f"AsideMovement.detect: error - Wrist landmark index out of bounds. Landmarks count: {len(landmarks)}")
            return None


        left_hand_y = left_wrist_coords[Y_COORDINATE_INDEX]
        right_hand_y = right_wrist_coords[Y_COORDINATE_INDEX]
        
        # print(f"AsideMovement.detect: input - L_y: {left_hand_y:.3f}, R_y: {right_hand_y:.3f}, state: {self.current_motion_state}, start_T: {self.START_THRESHOLD}, end_T: {self.END_THRESHOLD}")

        event_to_return: Optional[str] = None

        if self.current_motion_state == self.STATE_IDLE:
            # Check for START_RIGHT: left hand significantly lower than right hand (Y increases downwards)
            if (left_hand_y - right_hand_y) > self.START_THRESHOLD:
                self.current_motion_state = self.STATE_ACTIVE_RIGHT
                event_to_return = START_RIGHT
            # Check for START_LEFT: right hand significantly lower than left hand
            elif (right_hand_y - left_hand_y) > self.START_THRESHOLD:
                self.current_motion_state = self.STATE_ACTIVE_LEFT
                event_to_return = START_LEFT
        
        elif self.current_motion_state == self.STATE_ACTIVE_RIGHT:
            # Check for END_RIGHT: hands y diff is less than END_THRESHOLD
            if abs(left_hand_y - right_hand_y) < self.END_THRESHOLD:
                self.current_motion_state = self.STATE_IDLE
                event_to_return = END_RIGHT
        
        elif self.current_motion_state == self.STATE_ACTIVE_LEFT:
            # Check for END_LEFT: hands y diff is less than END_THRESHOLD
            if abs(left_hand_y - right_hand_y) < self.END_THRESHOLD:
                self.current_motion_state = self.STATE_IDLE
                event_to_return = END_LEFT
        
        if event_to_return:
            print(f"AsideMovement.detect: event - {event_to_return}, new_state: {self.current_motion_state}")
        # else:
            # print(f"AsideMovement.detect: no_event - state remains: {self.current_motion_state}")


        return event_to_return

    