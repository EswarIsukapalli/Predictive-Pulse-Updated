from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    predictions = db.relationship('Prediction', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Prediction(db.Model):
    """Prediction history model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Input data
    gender = db.Column(db.String(20), nullable=False)
    age = db.Column(db.String(20), nullable=False)
    history = db.Column(db.String(10), nullable=False)
    patient = db.Column(db.String(10), nullable=False)
    take_medication = db.Column(db.String(10), nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    breath_shortness = db.Column(db.String(10), nullable=False)
    visual_changes = db.Column(db.String(10), nullable=False)
    nose_bleeding = db.Column(db.String(10), nullable=False)
    whendiagnoused = db.Column(db.String(20), nullable=False)
    systolic = db.Column(db.String(20), nullable=False)
    diastolic = db.Column(db.String(20), nullable=False)
    controlled_diet = db.Column(db.String(10), nullable=False)
    
    # Additional health metrics
    height = db.Column(db.Float, nullable=True)  # in cm
    weight = db.Column(db.Float, nullable=True)  # in kg
    heart_rate = db.Column(db.Integer, nullable=True)
    
    # Prediction results
    stage_label = db.Column(db.String(50), nullable=False)
    stage_class = db.Column(db.String(20), nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
    risk_score = db.Column(db.Float, nullable=False)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<Prediction {self.stage_label} on {self.created_at}>'
