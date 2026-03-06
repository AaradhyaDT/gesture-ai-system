import mediapipe as mp
import numpy as np

class MLGestureModel:
    """MediaPipe-based Gesture Recognition using hand landmark analysis"""

    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )

    def classify(self, landmarks):
        """
        Classify gesture from hand landmarks using finger counting
        and position analysis - MediaPipe approach
        
        Returns: (gesture_name, confidence)
        """
        try:
            # Extract finger positions
            fingers_open = self._count_fingers(landmarks)
            thumb_open = fingers_open[0]
            fingers_count = sum(fingers_open)
            
            # Get key positions for gesture analysis
            wrist = landmarks[0]
            thumb_tip = landmarks[4]
            index_tip = landmarks[8]
            middle_tip = landmarks[12]
            
            # Gesture detection logic
            gesture = "UNKNOWN"
            confidence = 0.5
            
            # Closed Fist
            if fingers_count == 0:
                gesture = "FIST"
                confidence = 0.95
            
            # Open Palm - all fingers extended
            elif fingers_count == 5 and all(fingers_open):
                gesture = "OPEN_PALM"
                confidence = 0.95
            
            # Peace / Victory - only middle and index extended
            elif fingers_open == [0, 1, 1, 0, 0]:
                gesture = "PEACE"
                confidence = 0.90
            
            # Pointing - only index extended
            elif fingers_open == [0, 1, 0, 0, 0]:
                gesture = "POINTING"
                confidence = 0.85
            
            # Thumbs Up/Down - only thumb
            elif fingers_open == [1, 0, 0, 0, 0]:
                if thumb_tip.y < wrist.y:
                    gesture = "THUMB_UP"
                    confidence = 0.90
                else:
                    gesture = "THUMBS_DOWN"
                    confidence = 0.90
            
            # OK sign - thumb and index connected
            elif fingers_open == [1, 1, 1, 1, 1]:
                # Distance between thumb and index
                thumb_index_dist = np.sqrt(
                    (thumb_tip.x - index_tip.x) ** 2 + 
                    (thumb_tip.y - index_tip.y) ** 2
                )
                if thumb_index_dist < 0.05:
                    gesture = "OK_SIGN"
                    confidence = 0.85
                else:
                    gesture = "OPEN_PALM"
                    confidence = 0.90
            
            return gesture, confidence
            
        except Exception as e:
            return "UNKNOWN", 0.0

    def _count_fingers(self, landmarks):
        """
        Count which fingers are extended
        Returns list of 5 binary values [thumb, index, middle, ring, pinky]
        """
        # Tip and PIP joint indices
        tips = [4, 8, 12, 16, 20]
        pips = [3, 6, 10, 14, 18]
        
        fingers = []
        
        # Thumb: special logic based on hand orientation
        if landmarks[4].x < landmarks[3].x:
            fingers.append(1)  # Thumb extended
        else:
            fingers.append(0)
        
        # Other fingers: if tip is above PIP joint
        for tip, pip in zip(tips[1:], pips[1:]):
            if landmarks[tip].y < landmarks[pip].y:
                fingers.append(1)
            else:
                fingers.append(0)
        
        return fingers