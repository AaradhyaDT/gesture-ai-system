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
