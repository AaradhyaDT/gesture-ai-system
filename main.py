import cv2
import json
import warnings
import os

warnings.filterwarnings("ignore", category=UserWarning, module="google.protobuf")

from camera_config import init_camera, WINDOW_NAME, enforce_aspect_ratio
from serial_comm import SerialComm
from hand_detector import HandDetector
from gesture_logic import count_fingers, speed_from_fingers
from ml_gesture_model import MLGestureModel
from gesture_state_machine import GestureStateMachine
from dashboard import draw_dashboard
from logger_config import get_logger

logger = get_logger()

# ----------------------------
# Load configuration
# ----------------------------
CONFIG_FILE = "config.json"
config = {}

if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load {CONFIG_FILE}: {e}")

# ----------------------------
# Serial
# ----------------------------
serial_comm = SerialComm(logger)
serial_comm.connect(config)

# ----------------------------
# Camera
# ----------------------------
cap = init_camera()
if not cap.isOpened():
    logger.error("Camera failed")
    exit(1)

# ----------------------------
# Logic
# ----------------------------
detector = HandDetector()
ml = MLGestureModel()
gsm = GestureStateMachine()

speed = 0
prev_packet = ""

logger.info("System started")

# ----------------------------
# Main Loop
# ----------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        continue

    imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = detector.detect(imgRGB)

    dashboard_data = {}
    gesture_cmd = None

    if result.multi_hand_landmarks:
        hand_data = {}

        for i, hand in enumerate(result.multi_hand_landmarks):
            raw_label = result.multi_handedness[i].classification[0].label
            user_label = "Right" if raw_label == "Left" else "Left"

            # ============================
            # LEFT HAND → SPEED ONLY
            # ============================
            if user_label == "Left":
                gesture, confidence = ml.classify(hand.landmark)

                cmd = gsm.update("Left", gesture, confidence)
                if cmd:
                    gesture_cmd = cmd

                fingers = count_fingers(hand.landmark, raw_label)
                speed = speed_from_fingers(fingers)

                hand_data[user_label] = {
                    "Gesture": gesture,
                    "Confidence": confidence,
                    "Speed": speed,
                }

            # ============================
            # RIGHT HAND → COMMANDS ONLY
            # ============================
            else:
                gesture, confidence = ml.classify(hand.landmark)

                cmd = gsm.update("Right", gesture, confidence)
                if cmd:
                    gesture_cmd = cmd

                # right hand does not report speed at all
                hand_data[user_label] = {
                    "Gesture": gesture,
                    "Confidence": confidence,
                    "CMD": gesture_cmd if gesture_cmd else "-"
                }

            detector.draw(frame, hand)

        dashboard_data = hand_data

        # ----------------------------
        # Serial send
        # ----------------------------
        if gesture_cmd:
            speed_level = max(0, min(5, speed // 50))
            packet = f"{gesture_cmd},{speed_level}"

            if packet != prev_packet:
                serial_comm.send(packet + "\n")
                logger.info(f"Command sent: {packet}")
                prev_packet = packet

    # ----------------------------
    # UI
    # ----------------------------
    draw_dashboard(frame, dashboard_data)
    enforce_aspect_ratio()
    cv2.imshow(WINDOW_NAME, frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

# ----------------------------
# Cleanup
# ----------------------------
cap.release()
serial_comm.close()
cv2.destroyAllWindows()
logger.info("System stopped")
