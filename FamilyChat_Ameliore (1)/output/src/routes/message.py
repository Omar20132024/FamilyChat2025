from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from src.main import db, socketio
from src.models.message import Message
from src.models.user import User
from src.models.group import Group
from src.models.group_member import GroupMember
from datetime import datetime
import traceback

message_bp = Blueprint('message', __name__, url_prefix='/message')

@message_bp.route('/send', methods=['POST'])
@login_required
def send_message():
    try:
        data = request.json
        receiver_id = data.get('receiver_id')
        group_id = data.get('group_id')
        content = data.get('content')
        
        if not content:
            return jsonify({"status": "error", "message": "Le contenu du message est requis"}), 400
        
        if not receiver_id and not group_id:
            return jsonify({"status": "error", "message": "Destinataire ou groupe requis"}), 400
        
        # Création du message
        message = Message(
            sender_id=current_user.id,
            receiver_id=receiver_id,
            group_id=group_id,
            content=content
        )
        
        db.session.add(message)
        db.session.commit()
        
        # Émission via SocketIO
        message_data = message.to_dict()
        
        if receiver_id:
            # Message privé
            socketio.emit('new_private_message', message_data, room=f"user_{receiver_id}")
            socketio.emit('new_private_message', message_data, room=f"user_{current_user.id}")
        elif group_id:
            # Message de groupe
            socketio.emit('new_group_message', message_data, room=f"group_{group_id}")
        
        return jsonify({"status": "success", "message": "Message envoyé", "data": message_data})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@message_bp.route('/private/<int:user_id>', methods=['GET'])
@login_required
def get_private_messages(user_id):
    try:
        # Récupérer les messages entre l'utilisateur courant et l'utilisateur spécifié
        messages = Message.query.filter(
            ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
            ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
        ).order_by(Message.timestamp).all()
        
        # Marquer les messages non lus comme lus
        unread_messages = Message.query.filter_by(
            sender_id=user_id,
            receiver_id=current_user.id,
            read=False
        ).all()
        
        for message in unread_messages:
            message.read = True
        
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "messages": [message.to_dict() for message in messages]
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@message_bp.route('/group/<int:group_id>', methods=['GET'])
@login_required
def get_group_messages(group_id):
    try:
        # Vérifier que l'utilisateur est membre du groupe
        is_member = GroupMember.query.filter_by(
            user_id=current_user.id,
            group_id=group_id
        ).first()
        
        if not is_member:
            return jsonify({"status": "error", "message": "Vous n'êtes pas membre de ce groupe"}), 403
        
        # Récupérer les messages du groupe
        messages = Message.query.filter_by(group_id=group_id).order_by(Message.timestamp).all()
        
        return jsonify({
            "status": "success",
            "messages": [message.to_dict() for message in messages]
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
