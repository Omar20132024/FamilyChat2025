from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from src.main import db
from src.models.user import User
from src.models.contact import Contact
from werkzeug.utils import secure_filename
import os

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        
        # Vérification de l'unicité du nom d'utilisateur et de l'email
        user_check = User.query.filter_by(username=username).first()
        if user_check and user_check.id != current_user.id:
            flash('Ce nom d\'utilisateur est déjà utilisé', 'danger')
            return render_template('profile/edit.html')
        
        email_check = User.query.filter_by(email=email).first()
        if email_check and email_check.id != current_user.id:
            flash('Cette adresse email est déjà utilisée', 'danger')
            return render_template('profile/edit.html')
        
        # Mise à jour du profil
        current_user.username = username
        current_user.email = email
        
        # Gestion de la photo de profil
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename:
                # Utilisation du nom d'utilisateur comme nom de fichier pour éviter les conflits
                filename = secure_filename(current_user.username + os.path.splitext(file.filename)[1])
                file_path = os.path.join('src/static/images/profiles', filename)
                file.save(file_path)
                current_user.profile_picture = filename
        
        db.session.commit()
        flash('Profil mis à jour avec succès', 'success')
        return redirect(url_for('user.profile'))
    
    return render_template('profile/edit.html')

@user_bp.route('/search', methods=['GET'])
@login_required
def search_users():
    query = request.args.get('query', '')
    if len(query) < 3:
        return jsonify([])
    
    users = User.query.filter(User.username.like(f'%{query}%')).all()
    
    # Exclure l'utilisateur actuel et formater les résultats
    results = []
    for user in users:
        if user.id != current_user.id:
            results.append({
                'id': user.id,
                'username': user.username,
                'profile_picture': user.profile_picture,
                'is_contact': Contact.query.filter_by(user_id=current_user.id, contact_id=user.id).first() is not None
            })
    
    return jsonify(results)

@user_bp.route('/contacts', methods=['GET'])
@login_required
def contacts():
    user_contacts = Contact.query.filter_by(user_id=current_user.id).all()
    return render_template('profile/contacts.html', contacts=user_contacts)

@user_bp.route('/add_contact/<int:user_id>', methods=['POST'])
@login_required
def add_contact(user_id):
    if user_id == current_user.id:
        flash('Vous ne pouvez pas vous ajouter vous-même comme contact', 'danger')
        return redirect(url_for('user.search_users'))
    
    # Vérifier si l'utilisateur existe
    user = User.query.get_or_404(user_id)
    
    # Vérifier si le contact existe déjà
    existing_contact = Contact.query.filter_by(user_id=current_user.id, contact_id=user_id).first()
    if existing_contact:
        flash(f'{user.username} est déjà dans vos contacts', 'info')
        return redirect(url_for('user.contacts'))
    
    # Ajouter le contact
    new_contact = Contact(user_id=current_user.id, contact_id=user_id)
    db.session.add(new_contact)
    db.session.commit()
    
    flash(f'{user.username} a été ajouté à vos contacts', 'success')
    return redirect(url_for('user.contacts'))

@user_bp.route('/remove_contact/<int:contact_id>', methods=['POST'])
@login_required
def remove_contact(contact_id):
    contact = Contact.query.filter_by(id=contact_id, user_id=current_user.id).first_or_404()
    
    contact_username = User.query.get(contact.contact_id).username
    db.session.delete(contact)
    db.session.commit()
    
    flash(f'{contact_username} a été retiré de vos contacts', 'success')
    return redirect(url_for('user.contacts'))
