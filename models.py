from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    object_id = db.Column(db.Integer, unique=True, nullable=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Item {self.object_id}>'
