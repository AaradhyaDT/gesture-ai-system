import mediapipe as mp

mpHands = mp.solutions.hands
mpDraw = mp.solutions.drawing_utils

class HandDetector:
    def __init__(self):
        self.hands = mpHands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.5
        )

    def detect(self, imgRGB):
        return self.hands.process(imgRGB)

    def draw(self, frame, hand_landmarks):
        mpDraw.draw_landmarks(
            frame,
            hand_landmarks,
            mpHands.HAND_CONNECTIONS
        )
