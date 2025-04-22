from ultralytics import YOLO
import cv2
from simple_tracker import SimpleTracker

# Load YOLOv8 model
model = YOLO("yolov8n.pt")

# Create tracker
tracker = SimpleTracker()

# Start webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Detect objects with YOLO
    results = model(frame, stream=True)

    boxes = []
    for r in results:
        for obj in r.boxes:
            x1, y1, x2, y2 = obj.xyxy[0]
            boxes.append([int(x1), int(y1), int(x2), int(y2)])

    # Update tracker
    tracked_objects = tracker.update(boxes)

    # Draw tracking boxes
    for x1, y1, x2, y2, obj_id in tracked_objects:
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f'ID {obj_id}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.imshow("Tracked Objects", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
