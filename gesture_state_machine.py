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
