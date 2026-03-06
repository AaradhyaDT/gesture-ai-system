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
