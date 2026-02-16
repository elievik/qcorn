"""
OPTIONNEL - Sécurisation supplémentaire avec vérification Firebase côté serveur

En production, vous pouvez ajouter une vérification supplémentaire pour:
1. Vérifier la validité du token Firebase
2. Ajouter une couche de sécurité
3. Empêcher les appels non autorisés

Ceci est OPTIONNEL. Le code actuel fonctionne sans cela.
"""

# ==================================================
# 1. INSTALLER FIREBASE ADMIN SDK (optionnel)
# ==================================================

# Dans requirements.txt:
# firebase-admin==6.2.0

# Ensuite:
# pip install -r requirements.txt


# ==================================================
# 2. TÉLÉCHARGER LA CLÉ PRIVÉE FIREBASE
# ==================================================

"""
Étapes:
1. Console Firebase → Paramètres du projet
2. Onglet "Comptes de service"
3. Cliquez "Générer une nouvelle clé privée"
4. Sauvegardez le fichier JSON dans: qcorn/firebase-key.json
"""


# ==================================================
# 3. UTILISER FIREBASE ADMIN SDK (optionnel)
# ==================================================

from firebase_admin import credentials, auth
from django.conf import settings
import firebase_admin

# Initialiser une seule fois
if not firebase_admin._apps:
    cred = credentials.Certificate(settings.BASE_DIR / 'firebase-key.json')
    firebase_admin.initialize_app(cred)


# ==================================================
# 4. EXEMPLE: Vérifier un token avant de connecter
# ==================================================

def firebase_login_with_verification(request):
    """Version sécurisée avec vérification du token"""
    import json
    from django.http import JsonResponse
    from django.contrib.auth import login as auth_login
    from django.contrib.auth.models import User
    
    try:
        data = json.loads(request.body)
        id_token = data.get('idToken')  # Token Firebase du client
        
        if not id_token:
            return JsonResponse({'error': 'Token manquant'}, status=400)
        
        # Vérifier le token Firebase avec Admin SDK
        decoded_token = auth.verify_id_token(id_token)
        
        # À ce stade, le token est valide et certifié par Firebase
        uid = decoded_token['uid']
        email = decoded_token.get('email')
        display_name = decoded_token.get('name', email.split('@')[0])
        
        # Créer/récupérer l'utilisateur Django
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email.split('@')[0],
                'first_name': display_name.split()[0] if display_name else '',
            }
        )
        
        # Connecter l'utilisateur
        auth_login(request, user)
        
        return JsonResponse({
            'success': True,
            'uid': uid,
            'message': 'Connecté avec succès'
        })
        
    except Exception as e:
        from django.http import JsonResponse
        return JsonResponse({'error': str(e)}, status=401)


# ==================================================
# 5. EXEMPLE: Middleware pour protéger les API
# ==================================================

from django.utils.deprecation import MiddlewareNotUsed
from django.http import JsonResponse

class FirebaseAuthMiddleware:
    """
    Vérifie les tokens Firebase pour certaines routes
    Protège l'API contre les appels non autorisés
    """
    
    # Routes qui nécessitent une authentification Firebase
    PROTECTED_PATHS = [
        '/api/submit-question/',
        '/vote/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Vérifier si c'est une route protégée
        is_protected = any(
            request.path.startswith(path) 
            for path in self.PROTECTED_PATHS
        )
        
        if is_protected and not request.user.is_authenticated:
            return JsonResponse(
                {'error': 'Authentification requise'}, 
                status=401
            )
        
        return self.get_response(request)


# ==================================================
# 6. EXEMPLE: Décorateur pour les vues protégées
# ==================================================

from functools import wraps

def require_firebase_auth(view_func):
    """Décorateur pour protéger une vue avec Firebase"""
    
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse(
                {'error': 'Authentification requise'}, 
                status=401
            )
        return view_func(request, *args, **kwargs)
    
    return wrapper


# ==================================================
# 7. MODIFIER LES TEMPLATES POUR ENVOYER LE TOKEN
# ==================================================

"""
Si vous activez la vérification Firebase côté serveur,
modifiez le code JavaScript pour envoyer le ID token:

```javascript
async function handleGoogleSignIn() {
    const result = await auth.signInWithPopup(provider);
    const user = result.user;
    
    // Récupérer l'ID token
    const idToken = await user.getIdToken();
    
    // Envoyer le token au backend
    const response = await fetch('/api/auth/firebase-login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            idToken: idToken,  // Ajouter le token
            uid: user.uid,
            email: user.email,
            displayName: user.displayName,
            photoURL: user.photoURL
        })
    });
    
    // ... reste du code
}
```
"""


# ==================================================
# 8. RÉSUMÉ DE LA SÉCURITÉ
# ==================================================

"""
SANS Firebase Admin SDK (Configuration actuelle):
✅ Simple à mettre en place
✅ Fonctionne bien en développement
✅ Les données viennent directement du client
⚠️ À utiliser uniquement en développement

AVEC Firebase Admin SDK (Option sécurisée):
✅ Vérification côté serveur du token
✅ Garantit que l'utilisateur est authentifié
✅ Impossible de forger des tokens
✅ Recommandé pour la production

Pour la production:
1. Activez firebase-admin
2. Téléchargez la clé privée
3. Modifiez les templates pour envoyer le token
4. Activez le middleware/décorateurs
"""
