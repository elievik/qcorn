# 🚀 Guide de Déploiement QRoom sur Railway

## 📋 Vue d'ensemble

Ce guide explique comment déployer votre application Django QRoom sur **Railway.app**, une plateforme de déploiement moderne et simple.

**Préalables:**
- Compte Railway.app ([inscription gratuite](https://railway.app))
- Repository Git (GitHub, GitLab, Bitbucket)
- Code source déjà poussé sur Git

---

## 🎯 Étape 1 : Préparer votre repository

### 1.1 Vérifier les fichiers essentiels

```bash
# Ces fichiers doivent exister dans le root de votre projet:
ls -la | grep -E "(Procfile|runtime.txt|requirements.txt)"
```

✅ Vous avez tous ces fichiers!

### 1.2 Pousser les derniers changements sur Git

```bash
git add .
git commit -m "Préparation pour déploiement Railway"
git push origin main
```

---

## 🔧 Étape 2 : Configurer Railway

### 2.1 Se connecter à Railway

1. Allez sur [railway.app](https://railway.app)
2. Cliquez sur **"Sign in"** → **"GitHub"** (ou autre service)
3. Autorisez l'accès à votre compte GitHub

### 2.2 Créer un nouveau projet

1. Cliquez sur **"New Project"**
2. Sélectionnez **"Deploy from GitHub"**
3. Connectez votre repository `qcorn`
4. Autorisez Railway à accéder à vos repositories

### 2.3 Railway détecte automatiquement

✅ Railway détecte:
- `Procfile` → Comment démarrer l'app
- `requirements.txt` → Les dépendances Python
- `runtime.txt` → La version de Python

---

## 🗄️ Étape 3 : Configurer la Base de Données

### 3.1 Ajouter PostgreSQL

**Sur le dashboard Railway:**

1. Cliquez sur **"+ New Service"**
2. Sélectionnez **"PostgreSQL"**
3. Railway crée automatiquement une DB Postgres

### 3.2 Les variables d'environnement sont AUTO-GÉNÉRÉES

Railway crée automatiquement:
- `DATABASE_URL` - Chaîne de connexion PostgreSQL

---

## 🔐 Étape 4 : Variables d'Environnement

### 4.1 Ajouter les variables sur Railway

**Sur le dashboard Railway:**

1. Cliquez sur votre app Django
2. Allez à l'onglet **"Variables"**
3. Cliquez sur **"+ New Variable"**

### 4.2 Variables à ajouter

**Minimales (obligatoires):**

```
SECRET_KEY = [Générez une clé sécurisée - voir section 4.3]
DEBUG = False
ALLOWED_HOSTS = your-app.railway.app,*.railway.app
```

**Pour PostgreSQL:**

```
DB_ENGINE = django.db.backends.postgresql
```

(Railway configure automatiquement DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT via DATABASE_URL)

**Pour HTTPS (Production):**

```
SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
```

### 4.3 Générer une SECRET_KEY sécurisée

#### Méthode 1: Avec Django

```bash
python3 manage.py shell
```

Puis dans le shell Python:

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Copiez la clé générée → Ajoutez-la sur Railway

#### Méthode 2: En ligne

Utilisez un générateur en ligne comme [Django Secret Key Generator](https://docs.djangoproject.com/en/4.2/ref/settings/#secret-key)

### 4.4 Variables optionnelles

```
# Pour contrôler les workers gunicorn
WORKERS = 4
WORKER_CLASS = sync

# Pour désactiver les logs verbeux (optionnel)
LOG_LEVEL = info
```

---

## 🚀 Étape 5 : Déploiement

### 5.1 Déclencher le déploiement

Une fois les variables configurées:

1. **Option A**: Poussez du code sur GitHub
   ```bash
   git push origin main
   ```
   Railway redéploiera automatiquement

2. **Option B**: Cliquez sur **"Deploy"** manuellement depuis le dashboard Railway

### 5.2 Regarder les logs

```
Sur le dashboard Railway:
Onglet "Deploy" → Regardez la progression en temps réel
```

Railway exécutera:
1. `release` → `python manage.py migrate`
2. `web` → `gunicorn qcorn.wsgi`

Attendez le message: **"Status: Success"** ✅

---

## ✅ Étape 6 : Tester le déploiement

### 6.1 URL de l'app

Votre app est disponible à:
```
https://your-app.railway.app
```

(Trouvez votre URL exacte dans le dashboard Railway)

### 6.2 Tester les routes principales

- ✅ **Landing**: https://your-app.railway.app/
- ✅ **Login**: https://your-app.railway.app/login/
- ✅ **Register**: https://your-app.railway.app/register/
- ✅ **Dashboard** (après login): https://your-app.railway.app/dashboard/

### 6.3 Tester Firebase Google Auth

1. Allez sur `https://your-app.railway.app/login/`
2. Cliquez sur **"Continuer avec Google"**
3. Vérifiez que vous êtes redirigé vers le dashboard

---

## 🔧 Étape 7 : Configuration Firebase (Production)

⚠️ **IMPORTANT**: Par défaut, les clés Firebase sont dans les templates HTML.

### 7.1 Vérifier que Firebase fonctionne

Sur votre console Firebase:

1. Allez à **"Authentification"** → **"Paramètres"**
2. Ajoutez votre domaine Railway:
   ```
   https://your-app.railway.app
   ```

3. Sauvegardez et testez la connexion Google

### 7.2 Votre configuration Firebase

Les variables Firebase se trouvent dans:
- `accounts/templates/accounts/login.html` (ligne ~121)
- `accounts/templates/accounts/register.html` (ligne ~125)

Elles sont déjà configurées avec vos clés. ✅

---

## 🐛 Troubleshooting

### Erreur: "ModuleNotFoundError"

```
❌ Solution: Une dépendance manque dans requirements.txt
```

Vérifiez que tous vos packages y sont:
```bash
pip freeze > requirements.txt
git push
```

### Erreur: "Database connection refused"

```
❌ Solution: Les variables DB ne sont pas configurées
```

Vérifiez sur le dashboard Railway:
1. Vous avez ajouté PostgreSQL?
2. La variable `DB_ENGINE` = `django.db.backends.postgresql`?

### Erreur: "Staticfiles not found"

```
❌ Solution: Les fichiers statiques ne sont pas compilés
```

Dans le Procfile, vérifiez:
```
release: python manage.py migrate
web: gunicorn qcorn.wsgi
```

(Nous avons ajouté WhiteNoise pour servir les staticfiles automatiquement)

### Erreur: 500 Internal Server Error

1. Allez sur le dashboard Railway
2. Onglet **"Logs"**
3. Cherchez le message d'erreur détaillé
4. Corrigez et repoussez le code sur GitHub

---

## 📊 Monitoring & Logs

### Voir les logs en temps réel

**Sur le dashboard Railway:**

```
Onglet "Logs" → Voyez tous les événements en temps réel
```

Recherchez par filtre:
- `ERROR` - Pour les erreurs
- `WARNING` - Pour les avertissements
- `INFO` - Pour les informations générales

### Métriques de performance

**Onglet "Metrics":**
- CPU usage
- Memory usage
- Network I/O
- Requests/sec

---

## 💾 Sauvegarde de la base de données

### Exporter les données

**Option 1: Depuis Django**

```bash
python3 manage.py dumpdata > backup.json
```

**Option 2: Depuis pgAdmin (via Railway)**

Sur le dashboard Railway, cliquez sur PostgreSQL → Plugin "pgAdmin"

---

## 🔄 Mise à jour du code

Chaque fois que vous poussez du code:

```bash
git add .
git commit -m "Your message"
git push origin main
```

Railway redéploiera **automatiquement** en quelques secondes! 🚀

---

## 🎯 Prochaines étapes

- [ ] Vérifiez que le login/register fonctionne
- [ ] Testez la création de panels
- [ ] Vérifiez que les QR codes s'affichent
- [ ] Testez le mode public
- [ ] Configurez un domaine personnalisé (optionnel)

---

## 📞 Support

### Documentation utile

- [Railway Docs](https://docs.railway.app)
- [Django Deployment](https://docs.djangoproject.com/en/4.2/howto/deployment/)
- [Gunicorn Configuration](https://docs.gunicorn.org/)

### En cas de problème

1. **Vérifiez les logs** Railway → Onglet "Logs"
2. **Testez localement** `python3 manage.py runserver`
3. **Consultez Django docs** pour les erreurs Django
4. **Ouvrez une issue** sur GitHub

---

## 🎉 Félicitations!

Votre app QRoom est maintenant en **production**! 🚀

Partagez votre URL avec vos amis et commencez à organiser des sessions Q&A!

---

**Version**: 1.0  
**Date**: Février 2026  
**Framework**: Django 4.2.27  
**Hosting**: Railway.app
