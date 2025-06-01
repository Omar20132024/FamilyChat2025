from datetime import datetime
from src.main import db

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    read = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Message {self.id} from {self.sender_id} to {self.receiver_id or "group " + str(self.group_id)}>'
    
    def to_dict(self):
        """Convertit le message en dictionnaire pour l'API JSON"""
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'group_id': self.group_id,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'read': self.read,
            'sender_username': self.sender.username if self.sender else None,
            'sender_profile_picture': self.sender.profile_picture if self.sender else None
        }
