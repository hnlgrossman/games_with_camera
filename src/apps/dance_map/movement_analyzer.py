import numpy as np
import time
import logging
from typing import Optional, List, Tuple, Dict
import mediapipe as mp
from config import MovementConfig
from .movements.press_movement import PressMovement
# from .movements.base_movement import BaseMovement
import cv2

from src.base_movement_analyzer import BaseMovementAnalyzer

from src.constants import (
    LEFT_FOOT_INDEX, RIGHT_FOOT_INDEX, Z_COORDINATE_INDEX, X_COORDINATE_INDEX, Y_COORDINATE_INDEX
)

class MovementAnalyzer(BaseMovementAnalyzer):
    """Analyzes pose landmarks to detect specific movements"""
    
    def __init__(self, config: MovementConfig, mp_pose, debug: bool = False):
        super().__init__(config, mp_pose, debug)
        
        # Initialize movement detectors
        self.movement_detectors = [
            PressMovement(self, debug=True),
        ]

        self.is_feet_stable = False;
        self.required_feet_stable_frames = 150
        self.feet_stable_counter = 0

        # Threshold for feet proximity
        self.feet_proximity_threshold = 0.1
        # Threshold for feet movement
        self.feet_movement_threshold = 0.01

        self.required_stable_frames_per_30_fps = 4
        self.required_stable_frames = 4

        self.left_foot_square = None
        self.right_foot_square = None

        self.foot_stable_threshold = 0.007

        self.left_foot_stable = False
        self.left_foot_stable_counter = 0
        self.left_foot_unstable_counter = 0
       
        self.right_foot_stable = False
        self.right_foot_stable_counter = 0
        self.right_foot_unstable_counter = 0

        
        # Square mapping variables with individual dimensions
        self.square_size = 0.2  # Default size (used if individual dimensions aren't set)
        self.squares = {
            "center": {"x_min": 0, "x_max": 0, "z_min": 0, "z_max": 0, "width": 0.15, "height": self.square_size},
            "left": {"x_min": 0, "x_max": 0, "z_min": 0, "z_max": 0, "width": self.square_size, "height": 0.4},
            "right": {"x_min": 0, "x_max": 0, "z_min": 0, "z_max": 0, "width": self.square_size, "height": 0.4},
            "forward": {"x_min": 0, "x_max": 0, "z_min": 0, "z_max": 0, "width": self.square_size, "height": 0.4},
            "backward": {"x_min": 0, "x_max": 0, "z_min": 0, "z_max": 0, "width": self.square_size, "height": 0.4}
        }
        self.has_mapped_squares = False

    def _log_debug_info(self):
        """Override of base class method for custom debug logging"""
        if not self.debug:
            return
            
        # Log foot positions and distances
        left_foot = self.current_landmark_points[LEFT_FOOT_INDEX]
        right_foot = self.current_landmark_points[RIGHT_FOOT_INDEX]
        
        # Get X, Y and Z distances for both feet
        left_foot_x_dist, _ = self.get_points_distance(LEFT_FOOT_INDEX, X_COORDINATE_INDEX)
        left_foot_y_dist, _ = self.get_points_distance(LEFT_FOOT_INDEX, Y_COORDINATE_INDEX)
        left_foot_z_dist, _ = self.get_points_distance(LEFT_FOOT_INDEX, Z_COORDINATE_INDEX)
        right_foot_x_dist, _ = self.get_points_distance(RIGHT_FOOT_INDEX, X_COORDINATE_INDEX)
        right_foot_y_dist, _ = self.get_points_distance(RIGHT_FOOT_INDEX, Y_COORDINATE_INDEX)
        right_foot_z_dist, _ = self.get_points_distance(RIGHT_FOOT_INDEX, Z_COORDINATE_INDEX)
        
        self.logger.debug(f"MovementAnalyzer: Foot distances - Left X: {left_foot_x_dist:.4f}, Y: {left_foot_y_dist:.4f}, Z: {left_foot_z_dist:.4f}, Right X: {right_foot_x_dist:.4f}, Y: {right_foot_y_dist:.4f}, Z: {right_foot_z_dist:.4f}")

    def _update_feet_stability(self):
        """
        Updates is_feet_stable based on feet proximity and movement.
        Sets is_feet_stable to true when both feet are close to each other
        and not moving for self.required_feet_stable_frames frames.
        """
        # Calculate distance between feet in all dimensions
        left_foot = self.current_landmark_points[LEFT_FOOT_INDEX]
        right_foot = self.current_landmark_points[RIGHT_FOOT_INDEX]
        
        if self.debug:
            self.logger.debug(f"MovementAnalyzer: Left foot position: {left_foot}, Right foot position: {right_foot}")
            self.logger.debug(f"MovementAnalyzer: Using proximity threshold: {self.feet_proximity_threshold}, movement threshold: {self.feet_movement_threshold}")
        
        # Calculate Euclidean distance between feet
        feet_distance = np.linalg.norm(left_foot - right_foot)
        
        # Check movement of each foot using the points_distance dictionary
        left_foot_movement_x, left_direction_x = self.get_points_distance(LEFT_FOOT_INDEX, X_COORDINATE_INDEX)
        left_foot_movement_y, left_direction_y = self.get_points_distance(LEFT_FOOT_INDEX, Y_COORDINATE_INDEX)
        # left_foot_movement_z, left_direction_z = self.get_points_distance(LEFT_FOOT_INDEX, Z_COORDINATE_INDEX)
        
        right_foot_movement_x, right_direction_x = self.get_points_distance(RIGHT_FOOT_INDEX, X_COORDINATE_INDEX)
        right_foot_movement_y, right_direction_y = self.get_points_distance(RIGHT_FOOT_INDEX, Y_COORDINATE_INDEX)
        # right_foot_movement_z, right_direction_z = self.get_points_distance(RIGHT_FOOT_INDEX, Z_COORDINATE_INDEX)
        
        if self.debug:
            self.logger.debug(f"MovementAnalyzer: Left foot movement - X: {left_foot_movement_x:.4f} ({('smaller' if left_direction_x else 'larger')}), Y: {left_foot_movement_y:.4f} ({('smaller' if left_direction_y else 'larger')})")
            self.logger.debug(f"MovementAnalyzer: Right foot movement - X: {right_foot_movement_x:.4f} ({('smaller' if right_direction_x else 'larger')}), Y: {right_foot_movement_y:.4f} ({('smaller' if right_direction_y else 'larger')})")
        
        # Calculate total movement for each foot
        left_foot_movement = left_foot_movement_x + left_foot_movement_y
        right_foot_movement = right_foot_movement_x + right_foot_movement_y
        
        # Update individual foot stability status
        self._update_foot_stability(LEFT_FOOT_INDEX, left_foot_movement_x, left_foot_movement_y)
        self._update_foot_stability(RIGHT_FOOT_INDEX, right_foot_movement_x, right_foot_movement_y)

        if self.debug:
            self.logger.debug(f"MovementAnalyzer: Total movements - Left: {left_foot_movement:.4f}, Right: {right_foot_movement:.4f}, Distance between feet: {feet_distance:.4f}")
            self.logger.debug(f"MovementAnalyzer: Feet movement threshold: {self.feet_movement_threshold}")
        
        # Check if feet are close and not moving
        feet_close = feet_distance < self.feet_proximity_threshold
        left_foot_stable = left_foot_movement < self.feet_movement_threshold
        right_foot_stable = right_foot_movement < self.feet_movement_threshold
        
        if self.debug:
            self.logger.debug(f"MovementAnalyzer: Stability conditions - Feet close: {feet_close}, Left foot stable: {left_foot_stable}, Right foot stable: {right_foot_stable}")
        
        if (feet_close and left_foot_stable and right_foot_stable):
            
            self.feet_stable_counter += 1
            
            if self.debug:
                self.logger.debug(f"MovementAnalyzer: All stability conditions met! Feet stability counter: {self.feet_stable_counter}/{self.required_feet_stable_frames}")
                if self.feet_stable_counter % 10 == 0 or self.feet_stable_counter == 1:  # Print less frequently for long counts
                    self.logger.debug(f"MovementAnalyzer: Feet distance: {feet_distance:.4f}, Left movement: {left_foot_movement:.4f}, Right movement: {right_foot_movement:.4f}")
            
            # Check if stable for required frames
            if self.feet_stable_counter >= self.required_feet_stable_frames:
                was_stable = self.is_feet_stable
                self.is_feet_stable = True
                if self.debug:
                    if not was_stable:
                        self.logger.debug("MovementAnalyzer: STABILITY ACHIEVED - Feet are now stable")
                    else:
                        self.logger.debug("MovementAnalyzer: Feet remain stable")
        else:
            # Reset counter if feet are moving or not close
            if self.feet_stable_counter > 0:
                if self.debug:
                    self.logger.debug(f"MovementAnalyzer: Reset feet stability counter ({self.feet_stable_counter} frames). Reason(s): {'Feet too far apart' if not feet_close else ''}{', Left foot moving' if not left_foot_stable else ''}{', Right foot moving' if not right_foot_stable else ''}")
                self.feet_stable_counter = 0
                
            if self.is_feet_stable:
                self.is_feet_stable = False
                if self.debug:
                    self.logger.debug("MovementAnalyzer: STABILITY LOST - Feet are no longer stable")
                # Reset square mapping when stability is lost

    def _update_foot_stability(self, foot_index, x_movement, y_movement):
        """
        Updates the stability status for an individual foot based on x and y coordinate movement
        
        Args:
            foot_index (int): The index of the foot to check (LEFT_FOOT_INDEX or RIGHT_FOOT_INDEX)
            x_movement (float): The movement in x coordinate
            y_movement (float): The movement in y coordinate
        """
        # Check if x and y movements are below threshold
        is_foot_stable = (x_movement < self.foot_stable_threshold and 
                          y_movement < self.foot_stable_threshold)
        
        # Handle left foot
        if foot_index == LEFT_FOOT_INDEX:
            if is_foot_stable:
                # Only consider foot as stable if it was unstable for at least 2 frames
                if self.left_foot_unstable_counter >= 2 or self.left_foot_stable:
                    self.left_foot_stable_counter += 1
                    self.left_foot_stable = True
                    # Reset unstable counter when foot becomes stable
                    self.left_foot_unstable_counter = 0
            else:
                # Increment unstable counter
                self.left_foot_unstable_counter += 1
                if self.left_foot_stable_counter > 0:
                    self.left_foot_stable_counter = 0
                if self.left_foot_stable:
                    self.left_foot_stable = False
                          
        # Handle right foot
        elif foot_index == RIGHT_FOOT_INDEX:
            if is_foot_stable:
                # Only consider foot as stable if it was unstable for at least 2 frames
                if self.right_foot_unstable_counter >= 2 or self.right_foot_stable:
                    self.right_foot_stable_counter += 1
                    self.right_foot_stable = True
                    # Reset unstable counter when foot becomes stable
                    self.right_foot_unstable_counter = 0
            else:
                # Increment unstable counter
                self.right_foot_unstable_counter += 1
                if self.right_foot_stable_counter > 0:
                    self.right_foot_stable_counter = 0
                if self.right_foot_stable:
                    self.right_foot_stable = False

    def set_square_dimensions(self, square_name, width=None, height=None):
        """
        Set custom width and height for a specific square.
        
        Args:
            square_name (str): Name of the square to modify ("center", "left", "right", "forward", "backward")
            width (float): Custom width for the square (if None, uses current value)
            height (float): Custom height for the square (if None, uses current value)
        
        Returns:
            bool: True if successful, False if square_name is invalid
        """
        if square_name not in self.squares:
            if self.debug:
                self.logger.debug(f"MovementAnalyzer: Invalid square name '{square_name}'")
            return False
            
        if width is not None:
            self.squares[square_name]["width"] = width
            
        if height is not None:
            self.squares[square_name]["height"] = height
            
        # Reset mapping so squares will be recalculated with new dimensions
        self.has_mapped_squares = False
        
        if self.debug:
            self.logger.debug(f"MovementAnalyzer: Set '{square_name}' square dimensions to width={self.squares[square_name]['width']}, height={self.squares[square_name]['height']}")
        
        return True
    
    def set_all_square_dimensions(self, size):
        """
        Set the same width and height for all squares at once.
        
        Args:
            size (float): Size to use for all squares
        """
        for square_name in self.squares:
            self.squares[square_name]["width"] = size
            self.squares[square_name]["height"] = size
            
        self.square_size = size  # Update default size
        self.has_mapped_squares = False
        
        if self.debug:
            self.logger.debug(f"MovementAnalyzer: Set all squares to size {size}")

    def map_squares(self):
        """
        Maps 5 squares around the feet position:
        - Center square: where feet are located
        - Right square: to the right of center
        - Left square: to the left of center
        - Forward square: in front of center
        - Backward square: behind center
        """
        if self.has_mapped_squares:
            return
        
        # Calculate the center point between feet
        left_foot = self.current_landmark_points[LEFT_FOOT_INDEX]
        right_foot = self.current_landmark_points[RIGHT_FOOT_INDEX]
        center_x = (left_foot[X_COORDINATE_INDEX] + right_foot[X_COORDINATE_INDEX]) / 2
        center_z = (left_foot[Z_COORDINATE_INDEX] + right_foot[Z_COORDINATE_INDEX]) / 2
        
        # Define the center square
        center_width = self.squares["center"]["width"]
        center_height = self.squares["center"]["height"]
        half_width = center_width / 2
        half_height = center_height / 2
        
        self.squares["center"].update({
            "x_min": center_x - half_width,
            "x_max": center_x + half_width,
            "z_min": center_z - half_height,
            "z_max": center_z + half_height
        })
        
        # Define the right square
        right_width = self.squares["right"]["width"]
        right_height = self.squares["right"]["height"]
        self.squares["right"].update({
            "x_min": center_x + half_width,
            "x_max": center_x + half_width + right_width,
            "z_min": center_z - right_height / 2,
            "z_max": center_z + right_height / 2
        })
        
        # Define the left square
        left_width = self.squares["left"]["width"]
        left_height = self.squares["left"]["height"]
        self.squares["left"].update({
            "x_min": center_x - half_width - left_width,
            "x_max": center_x - half_width,
            "z_min": center_z - left_height / 2,
            "z_max": center_z + left_height / 2
        })
        
        # Define the forward square
        forward_width = self.squares["forward"]["width"]
        forward_height = self.squares["forward"]["height"]
        self.squares["forward"].update({
            "x_min": center_x - forward_width / 2,
            "x_max": center_x + forward_width / 2,
            "z_min": center_z - half_height - forward_height,
            "z_max": center_z - half_height
        })
        
        # Define the backward square
        backward_width = self.squares["backward"]["width"]
        backward_height = self.squares["backward"]["height"]
        self.squares["backward"].update({
            "x_min": center_x - backward_width / 2,
            "x_max": center_x + backward_width / 2,
            "z_min": center_z + half_height,
            "z_max": center_z + half_height + backward_height
        })
        
        self.has_mapped_squares = True
        print(f"Squares mapped around center point ({center_x:.4f}, {center_z:.4f})")
        for square_name, square in self.squares.items():
            print(f"Square '{square_name}': X [{square['x_min']:.4f} to {square['x_max']:.4f}], Z [{square['z_min']:.4f} to {square['z_max']:.4f}], Width: {square['width']:.2f}, Height: {square['height']:.2f}")

    def get_foot_square(self, foot_index):
        """
        Determines which square a foot is located in
        """
        if not self.has_mapped_squares:
            return "unknown"
            
        foot_point = self.current_landmark_points[foot_index]
        foot_x = foot_point[X_COORDINATE_INDEX]
        foot_z = foot_point[Z_COORDINATE_INDEX]
        
        for square_name, square in self.squares.items():
            if (square["x_min"] <= foot_x <= square["x_max"] and 
                square["z_min"] <= foot_z <= square["z_max"]):
                return square_name
                
        return "outside"

    def track_feet_squares(self):
        """
        Tracks which square each foot is located in and prints the information
        """
        if not self.has_mapped_squares:
            return
            
        left_foot_square = self.get_foot_square(LEFT_FOOT_INDEX)
        right_foot_square = self.get_foot_square(RIGHT_FOOT_INDEX)

        self.left_foot_square = left_foot_square if left_foot_square != "outside" else None
        self.right_foot_square = right_foot_square if right_foot_square != "outside" else None
        
        left_foot = self.current_landmark_points[LEFT_FOOT_INDEX]
        right_foot = self.current_landmark_points[RIGHT_FOOT_INDEX]
        
        if self.debug:
            # Log foot stability status
            self.logger.debug(f"MovementAnalyzer: Left foot stable: {self.left_foot_stable}, stable counter: {self.left_foot_stable_counter}, unstable counter: {self.left_foot_unstable_counter}")
            self.logger.debug(f"MovementAnalyzer: Right foot stable: {self.right_foot_stable}, stable counter: {self.right_foot_stable_counter}, unstable counter: {self.right_foot_unstable_counter}")
        
        # Original commented code below
        # if self.debug:
        #     if left_foot_square != "outside":
        #         print(f"Left foot located at ({left_foot[X_COORDINATE_INDEX]:.4f}, {left_foot[Z_COORDINATE_INDEX]:.4f}) is in the {left_foot_square} square")
        #         print(f"Left foot relative position - Top: {left_foot[Z_COORDINATE_INDEX] - self.squares[left_foot_square]['z_max']:.4f}, Bottom: {self.squares[left_foot_square]['z_min'] - left_foot[Z_COORDINATE_INDEX]:.4f}, Right: {self.squares[left_foot_square]['x_max'] - left_foot[X_COORDINATE_INDEX]:.4f}, Left: {left_foot[X_COORDINATE_INDEX] - self.squares[left_foot_square]['x_min']:.4f}")
            
        #     if right_foot_square != "outside":
        #         print(f"Right foot located at ({right_foot[X_COORDINATE_INDEX]:.4f}, {right_foot[Z_COORDINATE_INDEX]:.4f}) is in the {right_foot_square} square")
        #         print(f"Right foot relative position - Top: {right_foot[Z_COORDINATE_INDEX] - self.squares[right_foot_square]['z_max']:.4f}, Bottom: {self.squares[right_foot_square]['z_min'] - right_foot[Z_COORDINATE_INDEX]:.4f}, Right: {self.squares[right_foot_square]['x_max'] - right_foot[X_COORDINATE_INDEX]:.4f}, Left: {right_foot[X_COORDINATE_INDEX] - self.squares[right_foot_square]['x_min']:.4f}")

    def update_is_stable_general(self) -> bool:
        pass
    
    def update_before_detect(self, landmark_points):
        self.required_feet_stable_frames = self.get_per_30_fps(20)
        self._update_feet_stability()
        
        # Map squares and track feet positions when stability is achieved
        if self.is_feet_stable:
            self.map_squares()
        
        self.track_feet_squares()

            
        super().update_before_detect(landmark_points)

    def draw_squares(self, frame):
        """
        Draws the 5 squares on the frame.
        Maps the 3D coordinates (x, z) to 2D screen coordinates.
        """
        if not self.has_mapped_squares:
            return frame
            
        # Create a copy of the frame to draw on
        vis_frame = frame.copy()
        
        # Define colors for each square (BGR format)
        colors = {
            "center": (0, 255, 0),    # Green
            "left": (255, 0, 0),      # Blue
            "right": (0, 0, 255),     # Red
            "forward": (255, 255, 0), # Cyan
            "backward": (0, 255, 255), # Yellow
            "outside": (255, 0, 255)  # Magenta (default for feet outside squares)
        }
        
        # Get frame dimensions
        height, width = vis_frame.shape[:2]
        
        # Define scaling factors to convert world coordinates to pixel coordinates
        # These values might need adjustment based on your specific setup
        scale_factor = 200
        x_offset = width // 2
        z_offset = height // 2
        
        # Draw each square
        for square_name, square in self.squares.items():
            # Convert world coordinates to pixel coordinates
            x1 = int(square["x_min"] * scale_factor + x_offset)
            x2 = int(square["x_max"] * scale_factor + x_offset)
            z1 = int(square["z_min"] * scale_factor + z_offset)
            z2 = int(square["z_max"] * scale_factor + z_offset)
            
            # Draw rectangle
            cv2.rectangle(vis_frame, (x1, z1), (x2, z2), colors[square_name], 2)
            
            # Add label
            cv2.putText(vis_frame, square_name, (x1 + 5, z1 + 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors[square_name], 1)
        
        # Draw feet positions
        if self.current_landmark_points is not None:
            left_foot = self.current_landmark_points[LEFT_FOOT_INDEX]
            right_foot = self.current_landmark_points[RIGHT_FOOT_INDEX]
            
            # Convert feet positions to pixel coordinates
            left_foot_x = int(left_foot[X_COORDINATE_INDEX] * scale_factor + x_offset)
            left_foot_z = int(left_foot[Z_COORDINATE_INDEX] * scale_factor + z_offset)
            right_foot_x = int(right_foot[X_COORDINATE_INDEX] * scale_factor + x_offset)
            right_foot_z = int(right_foot[Z_COORDINATE_INDEX] * scale_factor + z_offset)
            
            # Get colors based on which square each foot is in
            left_foot_color = colors["outside"]  # Default color if outside any square
            right_foot_color = colors["outside"]  # Default color if outside any square
            
            # Set color based on the square if foot is in a square
            if self.left_foot_square and self.left_foot_square in colors:
                left_foot_color = colors[self.left_foot_square]
            
            if self.right_foot_square and self.right_foot_square in colors:
                right_foot_color = colors[self.right_foot_square]
            
            # Draw feet positions
            cv2.circle(vis_frame, (left_foot_x, left_foot_z), 5, left_foot_color, -1)
            cv2.circle(vis_frame, (right_foot_x, right_foot_z), 5, right_foot_color, -1)
            
            # Add labels with colors matching the squares
            cv2.putText(vis_frame, "L", (left_foot_x + 7, left_foot_z), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, left_foot_color, 1)
            cv2.putText(vis_frame, "R", (right_foot_x + 7, right_foot_z),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, right_foot_color, 1)
        
        # Draw a legend
        legend_x = 10
        legend_y = 30
        for square_name, color in colors.items():
            if square_name != "outside":  # Don't include "outside" in the legend
                cv2.putText(vis_frame, f"{square_name}", (legend_x, legend_y), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                legend_y += 20
            
        # Add foot legend with dynamic colors
        left_legend_color = colors["outside"]
        if self.left_foot_square and self.left_foot_square in colors:
            left_legend_color = colors[self.left_foot_square]
            
        right_legend_color = colors["outside"]
        if self.right_foot_square and self.right_foot_square in colors:
            right_legend_color = colors[self.right_foot_square]
            
        cv2.putText(vis_frame, f"Left Foot ({self.left_foot_square or 'outside'})", (legend_x, legend_y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, left_legend_color, 1)
        legend_y += 20
        cv2.putText(vis_frame, f"Right Foot ({self.right_foot_square or 'outside'})", (legend_x, legend_y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, right_legend_color, 1)
        
        return vis_frame

    def process_frame(self, frame):
        """
        Process the current frame and draw squares if mapped
        """
        # Draw squares on the frame if they are mapped
        if self.has_mapped_squares:
            frame = self.draw_squares(frame)
            
        return frame


    
            
