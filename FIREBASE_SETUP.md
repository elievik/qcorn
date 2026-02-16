# Configuration Firebase pour QRoom

## 📋 Prérequis

Vous devez avoir un projet Firebase créé sur la console Firebase (https://console.firebase.google.com/).

## 🔧 Étapes de configuration

### 1. Créer un projet Firebase

1. Allez sur https://console.firebase.google.com/
2. Cliquez sur "Créer un projet"
3. Nommez le projet (ex: "QRoom")
4. Attendez la création du projet

### 2. Activer l'authentification Google

1. Dans la console Firebase, allez à **Authentification** > **Méthode de connexion**
2. Cliquez sur **Google**
3. Activez Google et cliquez sur **Enregistrer**
4. Vous aurez besoin d'une adresse email de support

### 3. Récupérer les clés Firebase

1. Dans la console Firebase, cliquez sur l'icône ⚙️ > **Paramètres du projet**
2. Allez à l'onglet **Vos applications**
3. Cliquez sur l'icône **web** (</>) pour créer une application web
4. Copiez le bloc `firebaseConfig`:

```javascript
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT.appspot.com",
  messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
  appId: "YOUR_APP_ID",
  measurementId: "YOUR_MEASUREMENT_ID"
};
```

### 4. Configurer Django

#### Mettre à jour les templates

Remplacez `YOUR_*` par vos vraies valeurs dans :
- `accounts/templates/accounts/login.html` (ligne ~105)
- `accounts/templates/accounts/register.html` (ligne ~102)

Exemple:
```javascript
const firebaseConfig = {
    apiKey: "AIzaSyDx...",
    authDomain: "qroom-12345.firebaseapp.com",
    projectId: "qroom-12345",
    storageBucket: "qroom-12345.appspot.com",
    messagingSenderId: "123456789",
    appId: "1:123456789:web:abcdef123456",
    measurementId: "G-ABCDEF1234"
};
```

### 5. Configurer la redirection OAuth (Important!)

1. Dans la console Firebase, allez à **Authentification** > **Paramètres**
2. Copiez `YOUR_PROJECT.firebaseapp.com` 
3. Allez à **Identifiants OAuth** (Google Cloud Console)
4. Cliquez sur votre client OAuth pour web
5. Ajoutez ces URIs autorisés:
   - `http://localhost:8000`
   - `http://127.0.0.1:8000`
   - Votre domaine de production

## 🚀 Utilisation

### Connexion avec Google

1. Les utilisateurs cliquent sur "Continuer avec Google"
2. Une fenêtre pop-up s'ouvre pour la connexion Google
3. Une fois authentifiés, ils sont connectés à Django automatiquement
4. Ils sont redirigés vers `/dashboard/`

### Points clés

- ✅ Les utilisateurs sont créés automatiquement dans Django
- ✅ L'email est utilisé comme identifiant unique
- ✅ Le nom d'affichage Google est copié dans Django
- ✅ Les sessions Django sont créées automatiquement

## 🔐 Sécurité important

⚠️ **En production:**
- Déplacez `firebaseConfig` dans les variables d'environnement
- N'exposez pas votre `apiKey` publiquement
- Utilisez HTTPS obligatoirement
- Configurez les règles Firestore/Realtime Database

## 📱 Dépannage

### Erreur: "Cannot read properties of undefined (reading 'initializeApp')"
→ Vérifiez que les scripts Firebase sont chargés en priorité

### Erreur: "cors error" ou "origin not allowed"
→ Ajoutez votre domaine dans les URIs autorisés OAuth

### Erreur: "User does not exist" au login
→ L'utilisateur doit d'abord s'inscrire avec Google sur le formulaire d'inscription

## 📚 Ressources

- [Documentation Firebase Auth](https://firebase.google.com/docs/auth)
- [Firebase Console](https://console.firebase.google.com)
- [Google Cloud Console](https://console.cloud.google.com)
