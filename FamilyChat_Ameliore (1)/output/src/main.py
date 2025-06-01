import logging
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!

from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_migrate import Migrate
import traceback

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Initialisation des extensions
db = SQLAlchemy()
socketio = SocketIO()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///familychat.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True  # Log toutes les requêtes SQL
    
    # Initialisation des extensions avec l'application
    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    migrate.init_app(app, db)
    
    # Enregistrement explicite du user_loader
    from src.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        logger.debug(f"Loading user with ID: {user_id}")
        try:
            return User.query.get(int(user_id))
        except Exception as e:
            logger.error(f"Error loading user: {e}")
            logger.error(traceback.format_exc())
            return None
    
    # Initialisation des fichiers statiques
    try:
        from src.init_static import init_static_files
        with app.app_context():
            init_static_files()
    except Exception as e:
        logger.error(f"Error initializing static files: {e}")
        logger.error(traceback.format_exc())
    
    # Enregistrement des blueprints
    try:
        from src.routes.auth import auth_bp
        from src.routes.user import user_bp
        from src.routes.message import message_bp
        from src.routes.group import group_bp
        
        app.register_blueprint(auth_bp)
        app.register_blueprint(user_bp)
        app.register_blueprint(message_bp)
        app.register_blueprint(group_bp)
    except Exception as e:
        logger.error(f"Error registering blueprints: {e}")
        logger.error(traceback.format_exc())
    
    # Initialisation des WebSockets
    try:
        from src.socket import init_socketio
        init_socketio()
    except Exception as e:
        logger.error(f"Error initializing WebSockets: {e}")
        logger.error(traceback.format_exc())
    
    # Route principale
    @app.route('/')
    def index():
        logger.debug("Accessing index route")
        return render_template('index.html')
    
    # Route de diagnostic
    @app.route('/health')
    def health():
        logger.debug("Checking application health")
        try:
            # Vérifier la connexion à la base de données
            db_ok = False
            try:
                db.session.execute('SELECT 1')
                db_ok = True
            except Exception as e:
                logger.error(f"Database check failed: {e}")
            
            return jsonify({
                "status": "ok" if db_ok else "error",
                "version": "1.0.0",
                "database": "connected" if db_ok else "error",
                "environment": os.environ.get('FLASK_ENV', 'production')
            })
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            logger.error(traceback.format_exc())
            return jsonify({"status": "error", "message": str(e)}), 500
    
    # Gestionnaire d'erreurs pour les erreurs 404
    @app.errorhandler(404)
    def page_not_found(error):
        logger.warning(f"Page not found: {request.path}")
        return render_template('error.html', error="Page non trouvée"), 404
    
    # Gestionnaire d'erreurs pour les erreurs 500
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal Server Error: {error}")
        logger.error(f"Request: {request.path}")
        logger.error(traceback.format_exc())
        return render_template('error.html', error="Erreur interne du serveur"), 500
    
    # Création des tables de la base de données
    with app.app_context():
        try:
            logger.info("Creating database tables...")
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            logger.error(traceback.format_exc())
    
    return app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
