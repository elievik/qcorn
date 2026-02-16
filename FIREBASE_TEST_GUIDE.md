# 🧪 Guide de Test - Firebase Authentication

## ✅ Avant de commencer

1. ✅ Créez un projet Firebase
2. ✅ Activez l'authentification Google
3. ✅ Récupérez vos clés Firebase
4. ✅ Mettez à jour les templates avec vos clés

## 🚀 Tester localement

### 1. Lancer le serveur Django

```bash
cd /Users/koudzoelievikoum/qcorn
python3 manage.py runserver
```

Vous devriez voir:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

### 2. Tester la page de connexion

1. Allez à: http://localhost:8000/login
2. Vous devriez voir:
   - Formulaire classique Email/Mot de passe
   - Bouton "Continuer avec Google"
   - Lien vers la page d'inscription

### 3. Tester la page d'inscription

1. Allez à: http://localhost:8000/register
2. Vous devriez voir:
   - Formulaire classique Nom/Email/Mot de passe
   - Bouton "Google"
   - Lien vers la page de connexion

### 4. Cliquer sur "Google"

1. Cliquez sur le bouton Google
2. Une fenêtre pop-up devrait s'ouvrir
3. Si ça ne marche pas, vérifiez:
   - ❌ Les clés Firebase sont remplies
   - ❌ Firebase SDK est chargé
   - ❌ Les pop-ups sont bloqués

### 5. Se connecter avec Google

1. Dans la pop-up, entrez vos identifiants Google
2. Acceptez les permissions
3. Vous devriez être redirigé vers `/dashboard/`
4. Un nouvel utilisateur est créé dans Django

## 🔍 Vérifier que ça fonctionne

### Dans Django Admin

```bash
python3 manage.py createsuperuser
```

Puis allez à: http://localhost:8000/admin

1. Connectez-vous
2. Allez à Users
3. Vous devriez voir l'utilisateur créé avec Google

Exemple:
- Email: votre_email@gmail.com
- Username: votre_email
- First Name: Votre Prénom

## 📊 Tester les endpoints API

### Test Login

```bash
curl -X POST http://localhost:8000/api/auth/firebase-login/ \
  -H "Content-Type: application/json" \
  -d '{
    "uid": "test_uid_123",
    "email": "test@example.com",
    "displayName": "Test User",
    "photoURL": "https://..."
  }'
```

Réponse attendue:
```json
{
    "success": true,
    "message": "Connexion réussie",
    "user": {
        "id": 2,
        "email": "test@example.com",
        "username": "test",
        "display_name": "Test User"
    }
}
```

### Test Register

```bash
curl -X POST http://localhost:8000/api/auth/firebase-register/ \
  -H "Content-Type: application/json" \
  -d '{
    "uid": "new_uid_456",
    "email": "new@example.com",
    "displayName": "New User",
    "photoURL": "https://..."
  }'
```

## 🐛 Dépannage

### "Popup blocked"

**Problème:** La fenêtre Google s'ouvre pas

**Solutions:**
1. Vérifiez les paramètres des pop-ups du navigateur
2. Attendez que la page charge complètement
3. Assurez-vous que Firebase SDK est chargé

### "firebase is not defined"

**Problème:** Firebase SDK n'est pas trouvé

**Solution:**
Vérifiez que dans `login.html` ou `register.html`:
```html
<script src="https://www.gstatic.com/firebasejs/10.5.0/firebase-app.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.5.0/firebase-auth.js"></script>
```

Sont AVANT votre script qui utilise firebase.

### "CORS error"

**Problème:** Erreur de domaine

**Solutions:**
1. Dans Firebase Console → Authentification → Paramètres
2. Vérifiez que `http://localhost:8000` est dans:
   - Origines autorisées pour JavaScript
   - URIs de redirection autorisés

### "Auth/invalid-api-key"

**Problème:** Clé API invalide

**Solutions:**
1. Vérifiez que les clés dans login.html et register.html sont correctes
2. Copiez-collez directement de la console Firebase
3. Vérifiez qu'il n'y a pas d'espaces

## ✅ Checklist finale

- [ ] Projet Firebase créé
- [ ] Google auth activé
- [ ] Clés Firebase copiées dans les templates
- [ ] localhost:8000 dans les domaines autorisés
- [ ] Serveur Django lancé
- [ ] Page login/register charge sans erreur
- [ ] Bouton Google s'affiche
- [ ] Pop-up Google s'ouvre à la click
- [ ] Connexion fonctionne
- [ ] Utilisateur créé dans Django
- [ ] Redirection vers dashboard OK

## 🎯 Résultats attendus

### Après clic sur "Google":

1. ✅ Pop-up s'ouvre
2. ✅ Vous vous connectez avec Google
3. ✅ Pop-up se ferme
4. ✅ Redirection vers /dashboard/
5. ✅ Vous êtes connecté
6. ✅ Navigation latérale affiche vos panels

### Dans la base de données:

```
User id: 123
  email: votre@gmail.com
  username: votre
  first_name: Votre
  is_active: True
```

## 📞 Support

Si ça ne fonctionne pas:

1. Vérifiez la console du navigateur (F12)
2. Cherchez les erreurs en rouge
3. Dépannage selon le message d'erreur
4. Consultez FIREBASE_SETUP.md pour plus de détails

---

**Bon test!** 🚀
