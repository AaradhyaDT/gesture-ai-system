# SBR V5 - Smart Gesture Control System (MediaPipe Native)

## Overview
V5 is a gesture recognition system powered by **MediaPipe**, a cross-platform ML framework from Google. The system supports dual-hand control without requiring any model training:
- **LEFT HAND**: Speed control (finger counting) + real-time gesture feedback
- **RIGHT HAND**: Command generation (direct gesture-to-action mapping)

### Key Upgrade: MediaPipe Native Gesture Recognition
- **No Model Training Required**: Uses MediaPipe's built-in hand landmark detection
- **Real-Time Performance**: Optimized for live video processing
- **7 Core Gestures Supported**: FIST, OPEN_PALM, PEACE, POINTING, THUMB_UP, THUMBS_DOWN, OK_SIGN
- **Zero Configuration**: Works out-of-the-box with no gesture files or calibration needed
- **Gesture Confidence**: Returns 0.0-1.0 confidence for each detected gesture

### Gesture Recognition Details
| Gesture | Detection Method | Confidence |
|---------|------------------|-----------|
| FIST | All fingers closed | 0.95 |
| OPEN_PALM | All fingers extended | 0.95 |
| PEACE / VICTORY | Index + Middle extended | 0.90 |
| POINTING | Only index extended | 0.85 |
| THUMB_UP | Thumb up above wrist | 0.90 |
| THUMBS_DOWN | Thumb down below wrist | 0.90 |
| OK_SIGN | Thumb-index distance < 5% | 0.85 |
| UNKNOWN | No match | 0.5 |

### Workflow
1. **Run Directly**: Execute `main.py` — no setup needed
2. **Real-Time Display**: Dashboard shows gestures + confidence + speed
3. **Gesture Mapping**: GestureStateMachine converts gestures → commands → serial packets
4. **No Recalibration**: MediaPipe handles all detection internally

### Key Advantages Over ML Training
- ✅ Instant startup (no model loading)
- ✅ Works immediately without gesture data collection
- ✅ Consistent detection across users
- ✅ Smaller footprint (no ML models to store)
- ✅ Reduced dependencies (no sklearn/joblib needed)

---

## camera_config.py

import cv2
import json

with open("config.json") as f:
    CONFIG = json.load(f)

WINDOW_NAME = "Hand Debug"
ASPECT_RATIO = 16 / 9

_last_size = None

def init_camera():
    cap = cv2.VideoCapture(CONFIG.get("camera", {}).get("index", 0))

    # default resolution fallback to 1920x1200 if not specified
    width = CONFIG.get("camera", {}).get("width", 1920)
    height = CONFIG.get("camera", {}).get("height", 1200)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

    # Initial window size (16:9)
    cv2.resizeWindow(
        WINDOW_NAME,
        CONFIG["camera"]["width"],
        CONFIG["camera"]["height"]
    )

    return cap


def enforce_aspect_ratio():
    """
    Call this ONCE per frame from main loop
    """
    global _last_size

    try:
        _, _, w, h = cv2.getWindowImageRect(WINDOW_NAME)
    except:
        return

    if _last_size == (w, h):
        return

    _last_size = (w, h)

    expected_h = int(w / ASPECT_RATIO)
    expected_w = int(h * ASPECT_RATIO)

    # Decide which dimension user changed
    if abs(expected_h - h) > abs(expected_w - w):
        cv2.resizeWindow(WINDOW_NAME, w, expected_h)
    else:
        cv2.resizeWindow(WINDOW_NAME, expected_w, h)

## config.json

{
  "serial": {
    "baud": 9600,
    "port": "COM10"
  },

  "bluetooth": {
    "enabled": true,
    "baud": 9600,
    "name": "HC-05"
  },

  "camera": {
    "index": 0,
    "width": 1920,
    "height": 1200,
    "fps": 60
  },

  "gesture_map": {
    "0": "B",
    "1": "X",
    "2": "L",
    "3": "R",
    "4": "O",
    "5": "F"
  },

  "stability_frames": 6,

  "dashboard": {
    "font_scale": 0.1,
    "thickness": 1,
    "margin_top_ratio": 0.05,
    "margin_left_ratio": 0.01,
    "line_spacing_ratio": 0.04,
    "nested_indent_ratio": 0.03
  }
}

## dashboard.py
import cv2

BLACK = (0, 0, 0)
GRAY = (80, 80, 80)
GREEN = (0, 255, 0)

def draw_dashboard(frame, data, calibrate_mode=False):
    h, w = frame.shape[:2]

    # --- Layout constants ---
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = max(0.7, h / 900)
    thickness = 2
    line_h = int(h * 0.06)
    
    # Responsive dimensions
    padding = int(w * 0.02)
    bar_height = int(h * 0.025)
    bar_width = int(w * 0.20)
    section_spacing = int(line_h * 1.0)
    line_spacing = int(line_h * 0.5)
    
    # Column widths for side-by-side layout
    col_width = int(w / 2)
    start_y = int(h * 0.08)
    
    # --- Draw each hand in column layout ---
    col_index = 0
    for hand, values in data.items():
        x = padding + (col_index * col_width)
        y = start_y
        
        # Hand header
        header = f"{hand} HAND"
        cv2.putText(frame, header, (x, y),
                    font, scale, BLACK, thickness + 1)
        y += section_spacing
        
        # Gesture
        gesture = values.get("Gesture", "-")
        conf = values.get("Confidence", 0.0)
        
        cv2.putText(frame, f"Gesture: {gesture}", (x, y),
                    font, scale, BLACK, thickness)
        y += line_spacing
        
        # Confidence bar
        filled = int(bar_width * min(conf, 1.0))
        bar_y1 = y
        bar_y2 = y + bar_height
        
        cv2.rectangle(frame, (x, bar_y1), (x + bar_width, bar_y2),
                      GRAY, 1)
        cv2.rectangle(frame, (x, bar_y1), (x + filled, bar_y2),
                      GREEN, -1)
        
        cv2.putText(frame, f"{conf:.2f}",
                    (x + bar_width + 10, bar_y2),
                    font, scale * 0.7, BLACK, 1)
        y += section_spacing
        
        # Show Speed only for LEFT hand
        if hand == "Left":
            speed = values.get("Speed", "-")
            cv2.putText(frame, f"Speed: {speed}", (x, y),
                        font, scale, BLACK, thickness)
        else:
            # Show CMD only for RIGHT hand
            cmd = values.get("CMD", "-")
            cv2.putText(frame, f"CMD: {cmd}", (x, y),
                        font, scale, BLACK, thickness)
        
        col_index += 1

    # --- Calibration indicator ---
    if calibrate_mode:
        txt = "CALIBRATION MODE ACTIVE"
        cv2.putText(frame, txt,
                    (int(w * 0.25), int(h * 0.95)),
                    font, scale, BLACK, thickness + 1)


def draw_graph(frame, values, x, y, w, h, color):
    if len(values) < 2:
        return
    step = w / len(values)
    for i in range(1, len(values)):
        cv2.line(
            frame,
            (int(x+(i-1)*step), int(y+h-values[i-1])),
            (int(x+i*step), int(y+h-values[i])),
            color, 2
        )

## gesture_logic.py
import json

with open("config.json") as f:
    CONFIG = json.load(f)

def count_fingers(lm, hand_label):
    tips = [4, 8, 12, 16, 20]
    fingers = []

    # Thumb logic based on hand side
    if hand_label == "Right":
        fingers.append(1 if lm[4].x < lm[3].x else 0)
    else:
        fingers.append(1 if lm[4].x > lm[3].x else 0)

    # Other fingers
    for tip in tips[1:]:
        fingers.append(1 if lm[tip].y < lm[tip - 2].y else 0)

    return fingers

def gesture_to_cmd(fingers):
    """Return command based on config.json mapping"""
    total = sum(fingers)
    return CONFIG["gesture_map"].get(str(total), "0")

def speed_from_fingers(fingers):
    """Convert finger count to speed (0-255)"""
    return min(sum(fingers) * 50, 255)

## gesture_stability.py
from collections import deque
import json

with open("config.json") as f:
    CONFIG = json.load(f)

class GestureStability:
    def __init__(self):
        self.buffer = deque(maxlen=CONFIG["stability_frames"])

    def update(self, cmd):
        self.buffer.append(cmd)
        if self.buffer.count(cmd) == len(self.buffer):
            return cmd
        return None

## gesture_state_machine.py
import time
from collections import deque

class GestureStateMachine:
    def __init__(self):
        self.states = {"Left": "IDLE", "Right": "IDLE"}
        self.buffers = {"Left": deque(maxlen=8), "Right": deque(maxlen=8)}
        self.last_emit = {}
        self.last_time = {}

        self.priority = {
            "THUMBS_DOWN": 3,
            "FIST": 2,
            "OPEN_PALM": 2,
            "THUMB_UP": 1,
            "POINTING": 1,
            "PEACE": 1
        }

        self.cooldown = {
            "STOP": 1.2,
            "FORWARD": 0.6,
            "LEFT": 0.5,
            "RIGHT": 0.5,
            "BRAKE": 0.8
        }

        self.thresholds = {
            "THUMB_UP": 0.75,
            "THUMBS_DOWN": 0.75,
            "OPEN_PALM": 0.8,
            "FIST": 0.8,
            "POINTING": 0.7
        }

        self.map = {
            "THUMB_UP": "FORWARD",
            "THUMBS_DOWN": "STOP",
            "OPEN_PALM": "BRAKE",
            "FIST": "HOLD",
            "POINTING": "RIGHT",
            "PEACE": "LEFT"
        }

    def update(self, hand, gesture, conf):
        now = time.time()

        # Unknown → reset smoothing slowly
        if gesture == "UNKNOWN":
            self.buffers[hand].clear()
            return None

        # Threshold gate
        if conf < self.thresholds.get(gesture, 0.8):
            return None

        # Adaptive smoothing
        buf = self.buffers[hand]
        buf.append((gesture, conf))

        min_frames = 3 if conf > 0.9 else 6
        if len(buf) < min_frames:
            return None

        # Majority vote
        gestures = [g for g, _ in buf]
        g = max(set(gestures), key=gestures.count)

        cmd = self.map.get(g)
        if not cmd:
            return None

        # Priority override
        if self.last_emit.get(hand):
            prev = self.last_emit[hand]
            if self.priority.get(g, 0) < self.priority.get(prev, 0):
                return None

        # Cooldown
        last_t = self.last_time.get(cmd, 0)
        if now - last_t < self.cooldown.get(cmd, 0.5):
            return None

        self.last_emit[hand] = g
        self.last_time[cmd] = now
        buf.clear()
        return cmd

## hand_detector.py
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

## logger_config.py
import logging

def get_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler("gesture.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("GESTURE_CTRL")

## main.py
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
        enforce_aspect_ratio()
        cv2.imshow(WINDOW_NAME, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("c"):
            calibrate_mode = not calibrate_mode
        elif key == ord("q"):
            break

    # ----------------------------
    # Cleanup
    # ----------------------------
    cap.release()
    serial_comm.close()
    cv2.destroyAllWindows()
    logger.info("System stopped")

## ml_gesture_model.py
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

## ml_gesture.py
import math
import json
import os

CALIB_FILE = "gesture_calib.json"

class MLGesture:
    def __init__(self):
        self.calib = self._load_calib()

    def classify(self, lm):
        fingers = self._fingers(lm)
        wrist = lm[0]
        thumb = lm[4]

        # Default
        gesture = "UNKNOWN"
        confidence = 0.1

        # ---------- Rules ----------
        if fingers == [1,1,1,1,1]:
            gesture, confidence = "OPEN_PALM", 0.9

        elif fingers == [0,0,0,0,0]:
            gesture, confidence = "FIST", 0.9

        elif fingers == [0,1,1,0,0]:
            gesture, confidence = "PEACE", 0.85

        elif fingers == [1,0,0,0,0]:
            if thumb.y < wrist.y:
                gesture, confidence = "THUMB_UP", 0.85
            else:
                gesture, confidence = "THUMBS_DOWN", 0.85

        elif fingers == [0,1,0,0,0]:
            gesture, confidence = "POINTING", 0.8

        # ---------- Calibration boost ----------
        confidence += self.calib.get(gesture, 0.0)
        confidence = min(confidence, 0.99)

        return gesture, confidence

    def _fingers(self, lm):
        tips = [4, 8, 12, 16, 20]
        pips = [2, 6, 10, 14, 18]
        return [1 if lm[t].y < lm[p].y else 0 for t, p in zip(tips, pips)]

    def calibrate(self, gesture):
        self.calib[gesture] = self.calib.get(gesture, 0.0) + 0.03
        self._save_calib()

    def _load_calib(self):
        if os.path.exists(CALIB_FILE):
            return json.load(open(CALIB_FILE))
        return {}

    def _save_calib(self):
        json.dump(self.calib, open(CALIB_FILE, "w"), indent=2)

## ml_to_cmd.py
from collections import deque
import time

class MLCommandMapper:
    def __init__(
        self,
        min_confidence=0.7,
        stable_frames=5,
        lock_time=0.6
    ):
        self.min_confidence = min_confidence
        self.stable_frames = stable_frames
        self.lock_time = lock_time

        self.buffers = {
            "Left": deque(maxlen=stable_frames),
            "Right": deque(maxlen=stable_frames)
        }

        self.locks = {
            "Left": {"cmd": None, "time": 0},
            "Right": {"cmd": None, "time": 0}
        }

        self.gesture_map = {
            "THUMB_UP": "FORWARD",
            "THUMBS_DOWN": "STOP",
            "OPEN_PALM": "BRAKE",
            "FIST": "HOLD",
            "PEACE": "LEFT",
            "POINTING": "RIGHT"
        }

    def update(self, hand_label, gesture, confidence):
        if confidence < self.min_confidence:
            return None

        now = time.time()

        # Lock active?
        lock = self.locks[hand_label]
        if lock["cmd"] and (now - lock["time"] < self.lock_time):
            return None

        # Add to smoothing buffer
        self.buffers[hand_label].append(gesture)

        # Check stability
        if len(self.buffers[hand_label]) < self.stable_frames:
            return None

        if len(set(self.buffers[hand_label])) == 1:
            stable_gesture = gesture
            cmd = self.gesture_map.get(stable_gesture)

            if cmd:
                self.locks[hand_label] = {
                    "cmd": cmd,
                    "time": now
                }
                self.buffers[hand_label].clear()
                return cmd

        return None

## requirements.txt
absl-py==2.3.1
attrs==25.4.0
cffi==2.0.0
contourpy==1.3.2
cycler==0.12.1
flatbuffers==25.12.19
fonttools==4.61.1
joblib==1.4.2
kiwisolver==1.4.9
matplotlib==3.10.8
mediapipe==0.10.9
numpy==2.2.6
opencv-contrib-python==4.12.0.88
opencv-python==4.12.0.88
packaging==25.0
pillow==12.1.0
protobuf==3.20.3
pycparser==2.23
pyparsing==3.3.1
pyserial==3.5
python-dateutil==2.9.0.post0
scikit-learn==1.6.0
six==1.17.0
sounddevice==0.5.3

## serial_comm.py
import serial
import serial.tools.list_ports
import time
import logging

class SerialComm:
    def __init__(self, logger: logging.Logger, use_bluetooth=False):
        self.logger = logger
        self.ser = None
        self.use_bluetooth = use_bluetooth

    def connect(self, config=None):
        """
        Connect to the Arduino/ESP32 serial port.
        If config is None, tries to auto-detect.
        """
        if config is None:
            config = {"serial": {"port": None, "baud": 9600},
                      "bluetooth": {"baud": 9600}}
        
        if self.use_bluetooth:
            port = config.get("bluetooth_port", None)
            baud = config["bluetooth"]["baud"]
        else:
            port = config["serial"].get("port")
            baud = config["serial"].get("baud", 9600)

        # Auto-detect if port is None
        if not port:
            ports = [p.device for p in serial.tools.list_ports.comports()]
            if not ports:
                self.logger.error("No serial ports found")
                return
            port = ports[0]  # pick the first one
            self.logger.info(f"Auto-detected serial port: {port}")

        try:
            self.ser = serial.Serial(port, baud, timeout=0, write_timeout=0)
            time.sleep(2)  # allow Arduino to reset
            self.logger.info(f"Connected to {port} at {baud} baud")
        except Exception as e:
            self.logger.error(f"Failed to connect to {port}: {e}")
            self.ser = None

    def send(self, packet: str):
        """
        Send control packet. Non-blocking, safe if COM is open elsewhere.
        """
        if self.ser and self.ser.is_open:
            try:
                self.ser.write(packet.encode())
                self.ser.flush()
            except Exception as e:
                self.logger.warning(f"Failed to send packet: {e}")
        else:
            self.logger.debug("Serial not connected, skipping packet")

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.logger.info("Serial connection closed")
