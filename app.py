from flask import Flask, render_template, Response
import cv2
from ultralytics import YOLO
from simple_tracker import SimpleTracker
from models import db, InventoryItem
from datetime import datetime
import os

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DB
db.init_app(app)

# Load YOLOv8 model and tracker
model = YOLO("yolov8n.pt")
tracker = SimpleTracker()
cap = cv2.VideoCapture(0)

# Ensure object image save directory exists
os.makedirs("static/objects", exist_ok=True)

# Create tables before the first request
@app.before_first_request
def create_tables():
    with app.app_context():
        db.create_all()

# Frame generation function
def generate_frames():
    with app.app_context():
        while True:
            success, frame = cap.read()
            if not success:
                break

            results = model(frame, stream=True)
            boxes = []

            for r in results:
                for obj in r.boxes:
                    x1, y1, x2, y2 = obj.xyxy[0]
                    boxes.append([int(x1), int(y1), int(x2), int(y2)])

            tracked_objects = tracker.update(boxes)

            for x1, y1, x2, y2, obj_id in tracked_objects:
                item = InventoryItem.query.filter_by(object_id=obj_id).first()
                if item:
                    item.last_seen = datetime.utcnow()
                else:
                    item = InventoryItem(object_id=obj_id)
                    db.session.add(item)
                db.session.commit()

                # Draw bounding box and ID
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f'ID {obj_id}', (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                # ✅ Save cropped object image
                cropped = frame[y1:y2, x1:x2]
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S%f")
                filename = f'static/objects/object_{obj_id}_{timestamp}.jpg'
                cv2.imwrite(filename, cropped)

            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Homepage route
@app.route('/')
def index():
    with app.app_context():
        items = InventoryItem.query.all()
    return render_template('index.html', items=items)

# Live video stream route
@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
