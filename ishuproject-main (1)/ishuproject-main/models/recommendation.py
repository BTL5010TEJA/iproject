"""Recommendation model."""
from datetime import datetime
from models import db
import json


class Recommendation(db.Model):
    """Recommendation model for storing user recommendations."""
    
    __tablename__ = 'recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    food_items = db.Column(db.Text, default='[]')  # JSON array of food IDs
    trimester = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    interactions = db.relationship('UserInteraction', backref='recommendation', lazy='dynamic')
    
    def __repr__(self):
        return f'<Recommendation {self.id} for User {self.user_id}>'
    
    def get_food_items(self):
        """Get food items as a list."""
        try:
            return json.loads(self.food_items) if self.food_items else []
        except:
            return []
    
    def set_food_items(self, items_list):
        """Set food items from a list."""
        self.food_items = json.dumps(items_list)
    
    def to_dict(self):
        """Convert recommendation to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'food_items': self.get_food_items(),
            'trimester': self.trimester,
            'reason': self.reason,
            'created_at': self.created_at.isoformat()
        }
