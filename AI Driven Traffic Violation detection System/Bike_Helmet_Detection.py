import cv2
from ultralytics import YOLO
import numpy as np

# Load YOLO models
general_model = YOLO("yolov8m.pt")  # For detecting bicycle, motorcycle
helmet_model = YOLO("HELMET 2/HELMET 3/yolov8n.pt")  # Helmet detection model

# Target classes
bike_classes = ["bicycle", "motorcycle"]
helmet_classes = ["helmet"]  # Assuming the helmet model detects "helmet"

def draw_text_with_background(frame, text, position, font, scale, text_color, background_color, border_color, thickness=2, padding=5):
    """Draw text with background and border on the frame."""
    (text_width, text_height), baseline = cv2.getTextSize(text, font, scale, thickness)
    x, y = position

    cv2.rectangle(frame,
                  (x - padding, y - text_height - padding),
                  (x + text_width + padding, y + baseline + padding),
                  background_color,
                  cv2.FILLED)

    cv2.rectangle(frame,
                  (x - padding, y - text_height - padding),
                  (x + text_width + padding, y + baseline + padding),
                  border_color,
                  thickness)

    cv2.putText(frame, text, (x, y), font, scale, text_color, thickness, lineType=cv2.LINE_AA)

# Video input and output
cap = cv2.VideoCapture("Video1.mp4")
fps = cap.get(cv2.CAP_PROP_FPS)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('helmet_output.mp4', fourcc, fps, (1100, 700))

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Video processing finished.")
        break

    frame = cv2.resize(frame, (1100, 700))

    # Detect bikes
    general_results = general_model.predict(frame, conf=0.5)
    bikes = []

    for result in general_results:
        boxes = result.boxes.xyxy
        confs = result.boxes.conf
        classes = result.boxes.cls

        for box, conf, cls in zip(boxes, confs, classes):
            class_name = general_model.names[int(cls)]
            if class_name in bike_classes:
                x1, y1, x2, y2 = map(int, box)
                bikes.append((x1, y1, x2, y2))
                cv2.rectangle(frame, (x1, y1), (x2, y2), [0, 255, 0], 2)
                draw_text_with_background(frame, f"{class_name.capitalize()}, conf:{conf*100:.2f}%", (x1, y1 - 10), cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), (0, 0, 0), (0, 255, 0))

    # Detect helmets
    helmet_results = helmet_model.predict(frame, conf=0.5)
    helmets = []

    for result in helmet_results:
        boxes = result.boxes.xyxy
        confs = result.boxes.conf
        classes = result.boxes.cls

        for box, conf, cls in zip(boxes, confs, classes):
            class_name = helmet_model.names[int(cls)]
            if class_name in helmet_classes:
                x1, y1, x2, y2 = map(int, box)
                helmets.append((x1, y1, x2, y2))
                cv2.rectangle(frame, (x1, y1), (x2, y2), [0, 255, 255], 2)
                draw_text_with_background(frame, f"Helmet, conf:{conf*100:.2f}%", (x1, y1 - 10), cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), (0, 0, 0), (0, 255, 255))

    # Check for violations: Bike without helmet
    for bike in bikes:
        bx1, by1, bx2, by2 = bike
        bike_center = ((bx1 + bx2) // 2, (by1 + by2) // 2)
        has_helmet = False

        for helmet in helmets:
            hx1, hy1, hx2, hy2 = helmet
            # Check if helmet overlaps or is near the bike (simple proximity check)
            if abs(bike_center[0] - (hx1 + hx2) // 2) < 100 and abs(bike_center[1] - (hy1 + hy2) // 2) < 100:  # Adjust threshold as needed
                has_helmet = True
                break

        if not has_helmet:
            # Draw red box for no helmet
            cv2.rectangle(frame, (bx1, by1), (bx2, by2), [0, 0, 255], 3)
            draw_text_with_background(frame, "No Helmet", (bx1, by1 - 10), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255), (255, 255, 255), (0, 0, 255))

    out.write(frame)

cap.release()
out.release()
cv2.destroyAllWindows()
