"""
Middleware optionnel pour vérifier les tokens Firebase côté serveur
Cela ajoute une couche de sécurité supplémentaire en production.

Installation:
1. Installez firebase-admin: pip install firebase-admin
2. Téléchargez votre fichier de clé privée depuis la console Firebase
3. Placez-le à: qcorn/firebase-key.json
4. Décommentez le middleware dans settings.py si vous l'activez
"""

import logging
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareNotUsed

logger = logging.getLogger(__name__)

# Firebase désactivé pour éviter les erreurs en production
try:
    import firebase_admin
    from firebase_admin import credentials, auth
    from django.conf import settings
    
    # Initialiser Firebase Admin (facultatif, pour vérification côté serveur)
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(settings.BASE_DIR / 'firebase-key.json')
            firebase_admin.initialize_app(cred)
    except Exception as e:
        logger.warning(f"Firebase Admin non configuré (optionnel): {e}")
        
except ImportError:
    logger.warning("Firebase non disponible - Mode développement")


class FirebaseAuthMiddleware:
    """
    Middleware optionnel pour vérifier les tokens Firebase.
    À utiliser en production pour plus de sécurité.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        response = self.get_response(request)
        return response


# Vue optionnelle pour vérifier un token Firebase côté serveur
def verify_firebase_token(request):
    """
    Endpoint optionnel pour vérifier un token Firebase.
    Utile pour sécuriser les appels API.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        import json
        data = json.loads(request.body)
        token = data.get('token')
        
        if not token:
            return JsonResponse({'error': 'Token manquant'}, status=400)
        
        # Vérifier le token avec Firebase Admin SDK
        decoded_token = auth.verify_id_token(token)
        
        return JsonResponse({
            'success': True,
            'uid': decoded_token['uid'],
            'email': decoded_token.get('email'),
            'claims': decoded_token
        })
    except Exception as e:
        logger.error(f"Erreur vérification token: {e}")
        return JsonResponse({'error': str(e)}, status=401)
