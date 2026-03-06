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
