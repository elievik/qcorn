#!/bin/bash

echo "🚀 Déploiement sur Railway..."

# Variables pour Railway
export DEBUG=False
export ALLOWED_HOSTS="web-production-a522d.up.railway.app"
export SECURE_SSL_REDIRECT=True
export CSRF_COOKIE_SECURE=True
export SESSION_COOKIE_SECURE=True

echo "📦 Installation des dépendances..."
pip install -r requirements.txt

echo "🗄️ Migration de la base de données..."
python manage.py migrate

echo "📁 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput --clear

echo "✅ Déploiement terminé !"
