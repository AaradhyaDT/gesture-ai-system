import cv2

BLACK = (0, 0, 0)
GRAY = (80, 80, 80)
GREEN = (0, 255, 0)

def draw_dashboard(frame, data):
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
