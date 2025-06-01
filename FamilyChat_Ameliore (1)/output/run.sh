#!/bin/bash

# Script de démarrage pour FamilyChat
# Ce script initialise et lance l'application FamilyChat

# Vérifier si l'environnement virtuel existe, sinon le créer
if [ ! -d "venv" ]; then
    echo "Création de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activer l'environnement virtuel
source venv/bin/activate

# Installer ou mettre à jour les dépendances
echo "Installation des dépendances..."
pip install -r requirements.txt

# Exporter les variables d'environnement
export FLASK_APP=src/main.py
export FLASK_ENV=production

# Lancer l'application
echo "Démarrage de l'application FamilyChat..."
python -m src.main
