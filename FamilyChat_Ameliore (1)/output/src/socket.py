from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from src.main import socketio, logger
import traceback

def init_socketio():
    """Initialise les événements SocketIO pour la messagerie en temps réel"""
    
    @socketio.on('connect')
    def handle_connect():
        if current_user.is_authenticated:
            # Rejoindre une salle personnelle pour recevoir des messages privés
            join_room(f"user_{current_user.id}")
            logger.debug(f"User {current_user.username} connected to socket")
            emit('response', {'data': 'Connecté au serveur'})
        else:
            logger.warning("Unauthenticated user tried to connect to socket")
    
    @socketio.on('disconnect')
    def handle_disconnect():
        if current_user.is_authenticated:
            logger.debug(f"User {current_user.username} disconnected from socket")
    
    @socketio.on('join')
    def handle_join(data):
        """Gère l'entrée d'un utilisateur dans une salle de discussion"""
        try:
            room = data.get('room')
            if not room:
                return
            
            # Vérifier si c'est une salle de groupe
            if room.startswith('group_'):
                group_id = room.split('_')[1]
                # Ici, on pourrait vérifier si l'utilisateur est membre du groupe
                
            join_room(room)
            logger.debug(f"User {current_user.username} joined room {room}")
            emit('status', {'msg': f"{current_user.username} a rejoint la conversation"}, room=room)
        except Exception as e:
            logger.error(f"Error in handle_join: {str(e)}")
            logger.error(traceback.format_exc())
    
    @socketio.on('leave')
    def handle_leave(data):
        """Gère la sortie d'un utilisateur d'une salle de discussion"""
        try:
            room = data.get('room')
            if not room:
                return
                
            leave_room(room)
            logger.debug(f"User {current_user.username} left room {room}")
            emit('status', {'msg': f"{current_user.username} a quitté la conversation"}, room=room)
        except Exception as e:
            logger.error(f"Error in handle_leave: {str(e)}")
            logger.error(traceback.format_exc())
    
    @socketio.on('typing')
    def handle_typing(data):
        """Indique qu'un utilisateur est en train d'écrire"""
        try:
            room = data.get('room')
            if not room:
                return
                
            emit('user_typing', {
                'user_id': current_user.id,
                'username': current_user.username
            }, room=room)
        except Exception as e:
            logger.error(f"Error in handle_typing: {str(e)}")
            logger.error(traceback.format_exc())
