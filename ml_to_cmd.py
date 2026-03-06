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
