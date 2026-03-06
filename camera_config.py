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

