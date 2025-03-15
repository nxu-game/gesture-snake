"""
Gesture detector module - Implements hand tracking and gesture recognition
"""

import cv2
import mediapipe as mp
import numpy as np
import math
from collections import Counter


class GestureDetector:
    """
    Hand gesture detector using MediaPipe
    """
    def __init__(self):
        """
        Initialize the gesture detector
        """
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Coordinate axis direction vectors
        self.axes = {
            "UP": (0, -1),     # Up direction (negative y-axis)
            "RIGHT": (1, 0),   # Right direction (positive x-axis)
            "DOWN": (0, 1),    # Down direction (positive y-axis)
            "LEFT": (-1, 0)    # Left direction (negative x-axis)
        }
        
        # Direction related variables
        self.last_direction = None
        self.direction_buffer = []
        self.buffer_size = 3  # Reduced buffer size for better responsiveness
        
        # Direction change detection
        self.last_raw_direction = None
        self.direction_change_count = 0
        self.direction_change_threshold = 3  # Threshold for consecutive detection of same new direction
        
        # Debug information
        self.debug_info = {}
        
        # Indicator position
        self.indicator_pos = None
    
    def detect_direction(self, frame):
        """
        Detect hand gesture and determine direction based on the angle between thumb-index line and coordinate axes

        Args:
            frame (numpy.ndarray): Input image frame

        Returns:
            str: Detected direction ('UP', 'RIGHT', 'DOWN', 'LEFT') or None if no hand detected
        """
        # Convert to RGB format
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process image
        results = self.hands.process(rgb_frame)
        
        h, w, _ = frame.shape
        
        # Reset indicator position
        self.indicator_pos = None
        
        # Draw hand landmarks
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame, 
                    hand_landmarks, 
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
                
                # Get thumb and index finger key points
                thumb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
                index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
                
                # Calculate thumb and index finger coordinates (pixel coordinates)
                thumb_x, thumb_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
                index_x, index_y = int(index_tip.x * w), int(index_tip.y * h)
                
                # Calculate vector from thumb to index finger
                line_vector = (index_x - thumb_x, index_y - thumb_y)
                
                # Calculate vector length
                vector_length = math.sqrt(line_vector[0]**2 + line_vector[1]**2)
                
                # If vector length is too small, might be noise, use previous direction
                if vector_length < 10:
                    return self.last_direction
                
                # Calculate angles with each coordinate axis
                angles = {}
                for name, axis_vector in self.axes.items():
                    # Calculate dot product
                    dot_product = line_vector[0] * axis_vector[0] + line_vector[1] * axis_vector[1]
                    # Calculate cosine of angle
                    cos_angle = dot_product / (vector_length * math.sqrt(axis_vector[0]**2 + axis_vector[1]**2))
                    # Prevent floating point precision issues
                    cos_angle = max(-1, min(1, cos_angle))
                    # Calculate angle (radians)
                    angle = math.acos(cos_angle)
                    # Store angle
                    angles[name] = angle
                
                # Choose direction with smallest angle
                raw_direction = min(angles, key=angles.get)
                
                # Detect direction change
                if raw_direction != self.last_raw_direction:
                    # Direction changed, reset count
                    self.direction_change_count = 1
                    self.last_raw_direction = raw_direction
                else:
                    # Direction unchanged, increment count
                    self.direction_change_count += 1
                
                # If same new direction detected consecutively reaches threshold, update direction immediately
                if self.direction_change_count >= self.direction_change_threshold and raw_direction != self.last_direction:
                    # Clear buffer and update direction immediately
                    self.direction_buffer = [raw_direction] * self.buffer_size
                    self.last_direction = raw_direction
                else:
                    # Normal smoothing process
                    self.direction_buffer.append(raw_direction)
                    if len(self.direction_buffer) > self.buffer_size:
                        self.direction_buffer.pop(0)
                    
                    # Get most common direction in buffer
                    if self.direction_buffer:
                        counter = Counter(self.direction_buffer)
                        smoothed_direction = counter.most_common(1)[0][0]
                        self.last_direction = smoothed_direction
                
                # Set indicator position - at midpoint between thumb and index finger
                center_x = (thumb_x + index_x) // 2
                center_y = (thumb_y + index_y) // 2
                self.indicator_pos = (center_x, center_y)
                
                # Save debug information
                self.debug_info = {
                    "thumb": (thumb_x, thumb_y),
                    "index": (index_x, index_y),
                    "line_vector": line_vector,
                    "angles": angles,
                    "raw_direction": raw_direction,
                    "smoothed_direction": self.last_direction,
                    "change_count": self.direction_change_count
                }
                
                # Draw thumb and index finger connection line
                cv2.line(
                    frame,
                    (thumb_x, thumb_y),
                    (index_x, index_y),
                    (0, 255, 255),
                    2
                )
                
                # Draw direction indicator arrow
                if self.last_direction:
                    axis_vector = self.axes[self.last_direction]
                    end_x = center_x + axis_vector[0] * 100
                    end_y = center_y + axis_vector[1] * 100
                    
                    cv2.arrowedLine(
                        frame,
                        (center_x, center_y),
                        (int(end_x), int(end_y)),
                        (0, 255, 0),
                        3
                    )
                
                return self.last_direction
        
        return self.last_direction
    
    def get_indicator_position(self):
        """
        Get indicator position
        
        Returns:
            tuple: (x, y) indicator coordinates, or None if no hand detected
        """
        return self.indicator_pos
    
    def release(self):
        """
        Release resources
        """
        self.hands.close() 