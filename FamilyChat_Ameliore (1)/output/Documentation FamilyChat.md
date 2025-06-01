# Documentation FamilyChat

## Présentation

FamilyChat est une application de messagerie inspirée de WhatsApp mais sans nécessiter de numéro de téléphone. Elle permet aux utilisateurs de communiquer facilement avec leur famille et amis via un identifiant unique basé sur leur adresse email.

## Fonctionnalités principales

- **Authentification sans numéro de téléphone** : Inscription et connexion par email
- **Messagerie instantanée** : Communication en temps réel entre utilisateurs
- **Gestion des contacts** : Ajout et recherche de contacts par nom d'utilisateur
- **Groupes de discussion** : Création et gestion de conversations de groupe
- **Interface responsive** : Adaptation automatique sur mobile et desktop

## Accès à l'application

L'application est déployée et accessible à l'adresse suivante :
**URL permanente** : [https://r19hnincqqny.manus.space](https://r19hnincqqny.manus.space)

## Guide d'utilisation

### Inscription et connexion

1. Accédez à l'URL de l'application
2. Cliquez sur "Inscription" pour créer un nouveau compte
3. Renseignez votre nom d'utilisateur, email et mot de passe
4. Validez l'inscription puis connectez-vous avec vos identifiants

### Gestion des contacts

1. Une fois connecté, accédez à l'onglet "Contacts" dans le menu latéral
2. Cliquez sur "Ajouter un contact" pour rechercher des utilisateurs
3. Entrez le nom d'utilisateur de la personne que vous souhaitez ajouter
4. Cliquez sur "Ajouter" pour l'ajouter à vos contacts

### Messagerie

1. Depuis le tableau de bord ou la liste des contacts, cliquez sur un contact
2. Saisissez votre message dans la zone de texte en bas de l'écran
3. Appuyez sur le bouton d'envoi ou sur la touche Entrée pour envoyer
4. Les messages s'affichent en temps réel grâce à la technologie WebSocket

### Groupes de discussion

1. Accédez à l'onglet "Groupes" dans le menu latéral
2. Cliquez sur "Créer un groupe" pour démarrer un nouveau groupe
3. Donnez un nom au groupe et ajoutez des membres parmi vos contacts
4. Gérez les membres du groupe en cliquant sur l'icône des utilisateurs dans l'en-tête du chat

## Architecture technique

FamilyChat est développé avec les technologies suivantes :

- **Backend** : Flask (Python) avec Flask-SocketIO pour les messages instantanés
- **Base de données** : SQLite (développement) / SQLite (production)
- **Frontend** : HTML, CSS, JavaScript avec WebSockets
- **Authentification** : Flask-Login pour la gestion des sessions utilisateur

## Structure du projet

```
chat_app/
├── venv/                      # Environnement virtuel Python
├── src/
│   ├── main.py                # Point d'entrée de l'application
│   ├── models/                # Modèles de données
│   │   ├── user.py            # Modèle utilisateur
│   │   ├── message.py         # Modèle message
│   │   ├── contact.py         # Modèle contact
│   │   ├── group.py           # Modèle groupe
│   │   └── group_member.py    # Modèle membre de groupe
│   ├── routes/                # Routes API
│   │   ├── auth.py            # Routes d'authentification
│   │   ├── user.py            # Routes utilisateur
│   │   ├── message.py         # Routes message
│   │   └── group.py           # Routes groupe
│   ├── static/                # Fichiers statiques
│   │   ├── css/               # Styles CSS
│   │   ├── js/                # Scripts JavaScript
│   │   └── images/            # Images
│   ├── templates/             # Templates HTML
│   │   ├── auth/              # Pages d'authentification
│   │   ├── chat/              # Pages de messagerie
│   │   └── profile/           # Pages de profil
│   └── utils/                 # Utilitaires
│       ├── db.py              # Gestion de la base de données
│       └── socket.py          # Gestion des WebSockets
└── requirements.txt           # Dépendances Python
```

## Installation locale (pour développement)

Si vous souhaitez installer l'application en local pour la développer ou la personnaliser :

1. Clonez le dépôt du projet
2. Créez un environnement virtuel Python : `python -m venv venv`
3. Activez l'environnement virtuel :
   - Windows : `venv\Scripts\activate`
   - Linux/Mac : `source venv/bin/activate`
4. Installez les dépendances : `pip install -r requirements.txt`
5. Lancez l'application : `python -m src.main`
6. Accédez à l'application dans votre navigateur : `http://localhost:5000`

## Personnalisation

Vous pouvez personnaliser l'application en modifiant :

- Les styles CSS dans `src/static/css/`
- Les templates HTML dans `src/templates/`
- Les fonctionnalités backend dans les fichiers Python correspondants

## Sécurité

- Les mots de passe sont hashés avec bcrypt avant stockage
- Les sessions utilisateur sont gérées de manière sécurisée via Flask-Login
- L'application utilise HTTPS pour les communications

## Support et contact

Pour toute question ou assistance concernant l'application, n'hésitez pas à nous contacter.
