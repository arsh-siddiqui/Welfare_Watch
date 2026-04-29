from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='citizen')  # 'admin' or 'citizen'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Dataset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    filename = db.Column(db.String(300), nullable=False)
    columns = db.Column(db.Text)  # JSON string of column names
    row_count = db.Column(db.Integer, default=0)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)

class CitizenReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    scheme = db.Column(db.String(200), nullable=False)
    issue_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default='pending')  # pending, reviewed, resolved
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

class RiskRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    risk_score = db.Column(db.Float, default=0.0)
    risk_category = db.Column(db.String(30), default='Low')
    indicator_1 = db.Column(db.Float, default=0.0)
    indicator_2 = db.Column(db.Float, default=0.0)
    indicator_3 = db.Column(db.Float, default=0.0)
    indicator_4 = db.Column(db.Float, default=0.0)
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'), nullable=True)
    computed_at = db.Column(db.DateTime, default=datetime.utcnow)
