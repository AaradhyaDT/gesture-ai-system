# SBR V5 — Smart Gesture Control System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.9-green)](https://mediapipe.dev/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.12-red)](https://opencv.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

A real-time, dual-hand gesture recognition system for robot/vehicle control. Powered by **MediaPipe** hand landmark detection — no model training or calibration required. Gestures are mapped to serial commands sent to an Arduino/ESP32 over USB or Bluetooth (HC-05).

---

## ✨ Features

- **Dual-Hand Control** — Left hand sets speed (finger count); Right hand issues directional commands
- **7 Core Gestures** — FIST, OPEN\_PALM, PEACE, POINTING, THUMB\_UP, THUMBS\_DOWN, OK\_SIGN
- **No Training Required** — MediaPipe native landmark analysis; works out-of-the-box
- **Adaptive Smoothing** — `GestureStateMachine` with majority-vote buffering, priority override, and per-command cooldowns
- **Serial + Bluetooth** — Auto-detects COM port; supports HC-05 wireless connection
- **Live Dashboard** — Overlaid HUD showing gesture, confidence bar, speed, and command per hand
- **Configurable** — All parameters (port, camera, gesture map, stability frames) in `config.json`

---

## 🖐️ Gesture Reference

| Gesture | Hand | Detection Rule | Confidence | Command |
|---|---|---|---|---|
| THUMB\_UP | Right | Thumb up above wrist | 0.90 | FORWARD |
| THUMBS\_DOWN | Right | Thumb down below wrist | 0.90 | STOP |
| OPEN\_PALM | Right | All 5 fingers extended | 0.95 | BRAKE |
| FIST | Right | All fingers closed | 0.95 | HOLD |
| PEACE | Right | Index + Middle extended | 0.90 | LEFT |
| POINTING | Right | Only index extended | 0.85 | RIGHT |
| Finger Count (0–5) | Left | Counts extended fingers | — | Speed 0–255 |

---

## 📁 Project Structure

```
SBR-V5/
├── main.py                  # Entry point — main capture & control loop
├── config.json              # Runtime configuration
├── camera_config.py         # Camera init & 16:9 aspect ratio enforcement
├── hand_detector.py         # MediaPipe Hands wrapper
├── ml_gesture_model.py      # Landmark-based gesture classifier (MLGestureModel)
├── ml_gesture.py            # Rule-based fallback classifier with calibration
├── gesture_logic.py         # Finger counting & speed calculation
├── gesture_state_machine.py # Smoothing, priority, cooldown state machine
├── gesture_stability.py     # Rolling buffer stability filter
├── ml_to_cmd.py             # Command mapper with lock & confidence gate
├── dashboard.py             # OpenCV HUD overlay renderer
├── serial_comm.py           # Serial/Bluetooth send & auto-detect
├── logger_config.py         # Logging to file + stdout
└── requirements.txt         # Python dependencies
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Webcam
- Arduino/ESP32 with matching firmware (optional — system runs without serial)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/sbr-v5.git
cd sbr-v5

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Edit config.json to match your serial port and camera index
```

### Configuration (`config.json`)

```json
{
  "serial":    { "port": "COM10", "baud": 9600 },
  "bluetooth": { "enabled": true, "baud": 9600, "name": "HC-05" },
  "camera":    { "index": 0, "width": 1920, "height": 1200, "fps": 60 },
  "gesture_map": {
    "0": "B", "1": "X", "2": "L",
    "3": "R", "4": "O", "5": "F"
  },
  "stability_frames": 6
}
```

| Key | Description |
|---|---|
| `serial.port` | COM port of your microcontroller (`null` for auto-detect) |
| `camera.index` | Camera device index (0 = default webcam) |
| `stability_frames` | Frames required for a stable gesture lock |
| `gesture_map` | Maps finger count (0–5) to single-character command codes |

### Run

```bash
python main.py
```

Press **`Q`** to quit.

---

## 📡 Serial Packet Format

Commands are sent as plain text over serial:

```
FORWARD,3\n
STOP,0\n
LEFT,2\n
```

Format: `COMMAND,SPEED_LEVEL\n` where `SPEED_LEVEL` is 0–5 (derived from left-hand finger count).

---

## 🔧 Module Overview

| Module | Responsibility |
|---|---|
| `MLGestureModel` | Primary classifier — analyses MediaPipe landmarks to identify gestures with confidence scores |
| `GestureStateMachine` | Converts raw gesture stream into stable commands using adaptive smoothing, priority rules, and cooldowns |
| `GestureStability` | Rolling buffer that only emits a command when all recent frames agree |
| `MLCommandMapper` | Secondary command pipeline with confidence gate and per-hand lock timer |
| `SerialComm` | Non-blocking serial write with auto-detect and Bluetooth support |
| `HandDetector` | Thin MediaPipe wrapper handling RGB conversion and landmark drawing |
| `draw_dashboard` | Renders a two-column HUD (Left: gesture + speed, Right: gesture + command) |

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| `mediapipe` | 0.10.9 | Hand landmark detection |
| `opencv-python` | 4.12.0.88 | Camera capture & rendering |
| `numpy` | 2.2.6 | Landmark math |
| `pyserial` | 3.5 | Serial/Bluetooth communication |
| `scikit-learn` | 1.6.0 | (Available for future ML features) |

Full list: [`requirements.txt`](requirements.txt)

---

## 🛠️ Troubleshooting

**Camera not opening**
- Check `camera.index` in `config.json`. Try `1` or `2` for external cameras.

**Serial not connecting**
- Set `serial.port` explicitly (e.g. `"COM3"` on Windows, `"/dev/ttyUSB0"` on Linux).
- Ensure no other application (Arduino IDE Serial Monitor) is holding the port.

**Gestures not detected / low confidence**
- Ensure good, even lighting on your hands.
- Keep your hand within 40–70 cm of the camera for best landmark accuracy.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
