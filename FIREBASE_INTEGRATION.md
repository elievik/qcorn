# 🔐 Integration Firebase - Résumé Complet

## ✅ Ce qui a été fait

### 1. **Vue de connexion avec Firebase** (`accounts/views.py`)
- ✅ Fonction `firebase_login()` - Crée/synchronise utilisateur Django avec Firebase
- ✅ Fonction `firebase_register()` - Inscrit nouveaux utilisateurs via Google  
- ✅ Les deux endpoints reçoivent les données du client et créent la session Django

### 2. **Templates actualisés**
- ✅ `login.html` - Bouton "Continuer avec Google" avec Firebase SDK
- ✅ `register.html` - Bouton d'inscription Google avec Firebase SDK
- ✅ Scripts JavaScript intégrés pour gérer l'authentification

### 3. **Routes API** (`qcorn/urls.py`)
```
/api/auth/firebase-login/   → POST - Connexion utilisateur existant
/api/auth/firebase-register/ → POST - Inscription nouvel utilisateur
```

### 4. **Fichiers de configuration**
- ✅ `firebase_config.py` - Configuration Firebase (à remplir)
- ✅ `firebase_auth_utils.py` - Utilitaires optionnels pour vérification serveur
- ✅ `FIREBASE_SETUP.md` - Guide complet de configuration

## 🔄 Flux d'authentification

```
Utilisateur clique "Google"
        ↓
Firebase affiche la fenêtre Google
        ↓
Utilisateur se connecte avec Google
        ↓
Firebase retourne un ID token + infos utilisateur
        ↓
JavaScript envoie à /api/auth/firebase-login/ (ou register)
        ↓
Django crée/récupère l'utilisateur
        ↓
Django crée une session (auth_login)
        ↓
Redirection vers /dashboard/
```

## 📦 Installation des dépendances

```bash
pip install -r requirements.txt
```

Contient:
- Django==4.2.27
- firebase-admin==6.2.0 (optionnel, pour vérification serveur)
- python-decouple==3.8

## 🚀 Prochaines étapes

### 1. **Créer un projet Firebase**
   - Allez à https://console.firebase.google.com
   - Créez un nouveau projet

### 2. **Récupérer les clés Firebase**
   - Paramètres du projet → Vos applications → Web
   - Copiez le bloc `firebaseConfig`

### 3. **Configurer Django**
   - Mettez à jour `YOUR_*` dans `login.html` et `register.html`
   - Remplacez par vos vraies clés Firebase

### 4. **Configurer OAuth (Important!)**
   - Console Firebase → Authentification → Paramètres
   - Ajoutez vos domaines aux URIs autorisés
   
### 5. **Tester la connexion**
   ```bash
   python manage.py runserver
   ```
   - Allez à http://localhost:8000/login
   - Cliquez sur le bouton Google
   - Vérifiez que ça fonctionne !

## 🔒 Variables d'environnement (Production)

```bash
# .env
FIREBASE_API_KEY=votre_api_key
FIREBASE_AUTH_DOMAIN=votre_project.firebaseapp.com
FIREBASE_PROJECT_ID=votre_project_id
FIREBASE_STORAGE_BUCKET=votre_bucket
FIREBASE_MESSAGING_SENDER_ID=votre_sender_id
FIREBASE_APP_ID=votre_app_id
```

Puis dans les templates:
```html
<script>
    const firebaseConfig = {
        apiKey: "{{ firebase_api_key }}",
        authDomain: "{{ firebase_auth_domain }}",
        ...
    };
</script>
```

## 🧪 Tester les endpoints API

### Login
```bash
curl -X POST http://localhost:8000/api/auth/firebase-login/ \
  -H "Content-Type: application/json" \
  -d '{
    "uid": "firebase_uid",
    "email": "user@example.com",
    "displayName": "John Doe",
    "photoURL": "https://..."
  }'
```

### Register
```bash
curl -X POST http://localhost:8000/api/auth/firebase-register/ \
  -H "Content-Type: application/json" \
  -d '{
    "uid": "firebase_uid",
    "email": "newuser@example.com",
    "displayName": "Jane Doe",
    "photoURL": "https://..."
  }'
```

## 🐛 Dépannage courant

| Erreur | Solution |
|--------|----------|
| `Cannot read properties of undefined (reading 'initializeApp')` | Vérifiez que le script Firebase charge avant votre code |
| `CORS error` | Ajoutez votre domaine aux URIs autorisés dans Google Cloud |
| `User does not exist` | L'utilisateur doit s'inscrire d'abord sur /register |
| `Popup blocked` | Vérifiez que popup n'est pas bloquée par le navigateur |

## 📚 Documentation complète

- [Guide FIREBASE_SETUP.md](./FIREBASE_SETUP.md)
- [Documentation Firebase](https://firebase.google.com/docs/auth)
- [Documentation Django Authentication](https://docs.djangoproject.com/en/4.2/topics/auth/)

## 🎯 Fonctionnalités

✅ Connexion Google  
✅ Inscription Google  
✅ Synchronisation avec Django User  
✅ Sessions Django automatiques  
✅ Redirection intelligente  
✅ Gestion d'erreurs robuste  
✅ Compatible prod & dev  

## 🔗 Intégration avec l'app

- Les utilisateurs créés via Firebase sont des `User` Django standards
- Ils ont accès à tous les panels comme les autres utilisateurs
- Les données de profil (email, nom) sont synchronisées
- Les sessions Django fonctionnent normalement

---

**Installation complète!** 🎉

Les utilisateurs peuvent maintenant se connecter avec Google sans mot de passe!
