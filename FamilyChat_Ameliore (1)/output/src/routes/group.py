from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from src.main import db, socketio
from src.models.group import Group
from src.models.group_member import GroupMember
from src.models.user import User
from src.models.contact import Contact
import traceback

group_bp = Blueprint('group', __name__, url_prefix='/group')

@group_bp.route('/', methods=['GET'])
@login_required
def list_groups():
    # Récupérer tous les groupes dont l'utilisateur est membre
    user_groups = Group.query.join(GroupMember).filter(GroupMember.user_id == current_user.id).all()
    return render_template('chat/groups.html', groups=user_groups)

@group_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_group():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')
        member_ids = request.form.getlist('members')
        
        if not name:
            flash('Le nom du groupe est obligatoire', 'danger')
            return redirect(url_for('group.create_group'))
        
        try:
            # Créer le groupe
            new_group = Group(
                name=name,
                description=description,
                creator_id=current_user.id
            )
            db.session.add(new_group)
            db.session.flush()  # Pour obtenir l'ID du groupe
            
            # Ajouter le créateur comme admin
            creator_member = GroupMember(
                group_id=new_group.id,
                user_id=current_user.id,
                is_admin=True
            )
            db.session.add(creator_member)
            
            # Ajouter les autres membres
            for member_id in member_ids:
                if int(member_id) != current_user.id:  # Éviter les doublons
                    member = GroupMember(
                        group_id=new_group.id,
                        user_id=int(member_id)
                    )
                    db.session.add(member)
            
            db.session.commit()
            flash(f'Le groupe "{name}" a été créé avec succès', 'success')
            return redirect(url_for('group.view_group', group_id=new_group.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la création du groupe: {str(e)}', 'danger')
            return redirect(url_for('group.create_group'))
    
    # Récupérer les contacts pour les ajouter au groupe
    contacts = Contact.query.filter_by(user_id=current_user.id).all()
    contact_users = [User.query.get(contact.contact_id) for contact in contacts]
    
    return render_template('chat/create_group.html', contacts=contact_users)

@group_bp.route('/<int:group_id>', methods=['GET'])
@login_required
def view_group(group_id):
    # Vérifier que l'utilisateur est membre du groupe
    membership = GroupMember.query.filter_by(
        group_id=group_id,
        user_id=current_user.id
    ).first()
    
    if not membership:
        flash('Vous n\'êtes pas membre de ce groupe', 'danger')
        return redirect(url_for('group.list_groups'))
    
    group = Group.query.get_or_404(group_id)
    members = GroupMember.query.filter_by(group_id=group_id).all()
    
    return render_template('chat/group.html', group=group, members=members, is_admin=membership.is_admin)

@group_bp.route('/<int:group_id>/add_member', methods=['POST'])
@login_required
def add_member(group_id):
    # Vérifier que l'utilisateur est admin du groupe
    membership = GroupMember.query.filter_by(
        group_id=group_id,
        user_id=current_user.id,
        is_admin=True
    ).first()
    
    if not membership:
        flash('Vous n\'avez pas les droits pour ajouter des membres', 'danger')
        return redirect(url_for('group.view_group', group_id=group_id))
    
    user_id = request.form.get('user_id')
    
    if not user_id:
        flash('Utilisateur non spécifié', 'danger')
        return redirect(url_for('group.view_group', group_id=group_id))
    
    # Vérifier si l'utilisateur est déjà membre
    existing_member = GroupMember.query.filter_by(
        group_id=group_id,
        user_id=user_id
    ).first()
    
    if existing_member:
        flash('Cet utilisateur est déjà membre du groupe', 'info')
        return redirect(url_for('group.view_group', group_id=group_id))
    
    # Ajouter le membre
    new_member = GroupMember(
        group_id=group_id,
        user_id=int(user_id)
    )
    db.session.add(new_member)
    db.session.commit()
    
    user = User.query.get(user_id)
    flash(f'{user.username} a été ajouté au groupe', 'success')
    
    # Notification via SocketIO
    socketio.emit('group_update', {
        'type': 'member_added',
        'group_id': group_id,
        'user_id': user_id
    }, room=f"group_{group_id}")
    
    return redirect(url_for('group.view_group', group_id=group_id))

@group_bp.route('/<int:group_id>/remove_member/<int:member_id>', methods=['POST'])
@login_required
def remove_member(group_id, member_id):
    # Vérifier que l'utilisateur est admin du groupe
    membership = GroupMember.query.filter_by(
        group_id=group_id,
        user_id=current_user.id,
        is_admin=True
    ).first()
    
    if not membership:
        flash('Vous n\'avez pas les droits pour retirer des membres', 'danger')
        return redirect(url_for('group.view_group', group_id=group_id))
    
    member = GroupMember.query.filter_by(id=member_id, group_id=group_id).first_or_404()
    
    # Empêcher la suppression du créateur
    group = Group.query.get(group_id)
    if member.user_id == group.creator_id:
        flash('Impossible de retirer le créateur du groupe', 'danger')
        return redirect(url_for('group.view_group', group_id=group_id))
    
    user = User.query.get(member.user_id)
    db.session.delete(member)
    db.session.commit()
    
    flash(f'{user.username} a été retiré du groupe', 'success')
    
    # Notification via SocketIO
    socketio.emit('group_update', {
        'type': 'member_removed',
        'group_id': group_id,
        'user_id': member.user_id
    }, room=f"group_{group_id}")
    
    return redirect(url_for('group.view_group', group_id=group_id))

@group_bp.route('/<int:group_id>/leave', methods=['POST'])
@login_required
def leave_group(group_id):
    membership = GroupMember.query.filter_by(
        group_id=group_id,
        user_id=current_user.id
    ).first_or_404()
    
    group = Group.query.get(group_id)
    
    # Empêcher le créateur de quitter le groupe
    if current_user.id == group.creator_id:
        flash('En tant que créateur, vous ne pouvez pas quitter le groupe. Vous devez le supprimer.', 'danger')
        return redirect(url_for('group.view_group', group_id=group_id))
    
    db.session.delete(membership)
    db.session.commit()
    
    flash(f'Vous avez quitté le groupe "{group.name}"', 'success')
    
    # Notification via SocketIO
    socketio.emit('group_update', {
        'type': 'member_left',
        'group_id': group_id,
        'user_id': current_user.id
    }, room=f"group_{group_id}")
    
    return redirect(url_for('group.list_groups'))

@group_bp.route('/<int:group_id>/delete', methods=['POST'])
@login_required
def delete_group(group_id):
    group = Group.query.get_or_404(group_id)
    
    # Vérifier que l'utilisateur est le créateur du groupe
    if group.creator_id != current_user.id:
        flash('Seul le créateur peut supprimer le groupe', 'danger')
        return redirect(url_for('group.view_group', group_id=group_id))
    
    group_name = group.name
    
    # Notification via SocketIO avant suppression
    socketio.emit('group_update', {
        'type': 'group_deleted',
        'group_id': group_id
    }, room=f"group_{group_id}")
    
    db.session.delete(group)  # Supprime également les membres et messages (cascade)
    db.session.commit()
    
    flash(f'Le groupe "{group_name}" a été supprimé', 'success')
    return redirect(url_for('group.list_groups'))
