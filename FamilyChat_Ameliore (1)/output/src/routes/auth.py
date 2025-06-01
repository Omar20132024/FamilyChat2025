from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from src.main import db, logger
from src.models.user import User
from datetime import datetime
import traceback

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    logger.debug("Accessing register route")
    
    try:
        if current_user.is_authenticated:
            return redirect(url_for('chat.dashboard'))
            
        if request.method == 'POST':
            logger.debug("Processing POST request for registration")
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            logger.debug(f"Registration attempt for username: {username}, email: {email}")
            
            # Validation des données
            if not username or not email or not password:
                flash('Tous les champs sont obligatoires', 'danger')
                return render_template('auth/register.html')
            
            if password != confirm_password:
                flash('Les mots de passe ne correspondent pas', 'danger')
                return render_template('auth/register.html')
            
            # Vérification de l'unicité du nom d'utilisateur et de l'email
            existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
            if existing_user:
                if existing_user.username == username:
                    flash('Ce nom d\'utilisateur est déjà utilisé', 'danger')
                else:
                    flash('Cette adresse email est déjà utilisée', 'danger')
                return render_template('auth/register.html')
            
            # Création du nouvel utilisateur
            try:
                logger.debug(f"Creating new user: {username}, {email}")
                new_user = User(
                    username=username,
                    email=email,
                    profile_picture='default.jpg'  # Utilisation d'une image par défaut
                )
                new_user.password = password  # Le hash est géré par le setter dans le modèle
                
                logger.debug("Adding user to database session")
                db.session.add(new_user)
                logger.debug("Committing database transaction")
                db.session.commit()
                logger.info(f"User registered successfully: {username}")
                
                flash('Inscription réussie ! Vous pouvez maintenant vous connecter', 'success')
                return redirect(url_for('auth.login'))
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error during user registration: {str(e)}")
                logger.error(traceback.format_exc())
                flash('Une erreur est survenue lors de l\'inscription. Veuillez réessayer.', 'danger')
                return render_template('auth/register.html')
        
        return render_template('auth/register.html')
    except Exception as e:
        logger.error(f"Unexpected error in register route: {str(e)}")
        logger.error(traceback.format_exc())
        return render_template('error.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    logger.debug("Accessing login route")
    
    try:
        if current_user.is_authenticated:
            return redirect(url_for('chat.dashboard'))
        
        if request.method == 'POST':
            logger.debug("Processing POST request for login")
            email = request.form.get('email')
            password = request.form.get('password')
            remember = True if request.form.get('remember') else False
            
            logger.debug(f"Login attempt for email: {email}")
            
            user = User.query.filter_by(email=email).first()
            
            if not user or not user.verify_password(password):
                flash('Identifiants incorrects', 'danger')
                return render_template('auth/login.html')
            
            # Mise à jour du statut et de la dernière connexion
            user.status = 'online'
            user.last_seen = datetime.utcnow()
            db.session.commit()
            
            login_user(user, remember=remember)
            logger.info(f"User logged in: {user.username}")
            return redirect(url_for('chat.dashboard'))
        
        return render_template('auth/login.html')
    except Exception as e:
        logger.error(f"Unexpected error in login route: {str(e)}")
        logger.error(traceback.format_exc())
        return render_template('error.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logger.debug("Accessing logout route")
    
    try:
        if current_user.is_authenticated:
            username = current_user.username
            current_user.status = 'offline'
            current_user.last_seen = datetime.utcnow()
            db.session.commit()
            
            logout_user()
            logger.info(f"User logged out: {username}")
            flash('Vous avez été déconnecté', 'info')
        
        return redirect(url_for('auth.login'))
    except Exception as e:
        logger.error(f"Unexpected error in logout route: {str(e)}")
        logger.error(traceback.format_exc())
        return render_template('error.html')
