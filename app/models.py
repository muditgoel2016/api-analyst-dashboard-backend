from app import db
from datetime import datetime

class LogEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(120), nullable=False, index=True)  # Indexed for efficient querying
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)  # Indexed for time-based queries
    status = db.Column(db.String(50), nullable=False, index=True)  # Indexed if query based on status
    error_message = db.Column(db.Text, nullable=True)
    request = db.Column(db.Text, nullable=True)
    response = db.Column(db.Text, nullable=True)