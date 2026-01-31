"""User model."""
from datetime import datetime
from flask_login import UserMixin
from models import db
import json


class User(UserMixin, db.Model):
    """User model for authentication and profile management."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    current_trimester = db.Column(db.Integer, default=1)
    health_conditions = db.Column(db.Text, default='{}')  # JSON string
    dietary_preferences = db.Column(db.String(50), default='vegetarian')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    recommendations = db.relationship('Recommendation', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    interactions = db.relationship('UserInteraction', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def get_health_conditions(self):
        """Get health conditions as a dictionary."""
        try:
            return json.loads(self.health_conditions) if self.health_conditions else {}
        except:
            return {}
    
    def set_health_conditions(self, conditions_dict):
        """Set health conditions from a dictionary."""
        self.health_conditions = json.dumps(conditions_dict)
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'current_trimester': self.current_trimester,
            'health_conditions': self.get_health_conditions(),
            'dietary_preferences': self.dietary_preferences,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
