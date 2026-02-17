import os
import firebase_admin
from firebase_admin import credentials
from django.conf import settings

def initialize_firebase():
    """
    Initialise Firebase Admin SDK avec les variables d'environnement
    """
    try:
        # Vérifier si Firebase est déjà initialisé
        if not firebase_admin._apps:
            # Configuration Firebase depuis les variables d'environnement
            firebase_config = {
                "type": "service_account",
                "project_id": os.getenv('FIREBASE_PROJECT_ID', 'qroom-bb7db'),
                "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID', ''),
                "private_key": os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
                "client_email": os.getenv('FIREBASE_CLIENT_EMAIL', ''),
                "client_id": os.getenv('FIREBASE_CLIENT_ID', ''),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_X509_CERT_URL', '')
            }
            
            # En développement, utiliser le fichier de service si disponible
            if settings.DEBUG and os.path.exists('serviceAccountKey.json'):
                cred = credentials.Certificate('serviceAccountKey.json')
            else:
                # Utiliser la configuration depuis les variables d'environnement
                if firebase_config["private_key"] and firebase_config["client_email"]:
                    cred = credentials.Certificate(firebase_config)
                else:
                    # En développement sans clé privée, utiliser une configuration par défaut
                    # Note: Cela ne fonctionnera pas en production
                    print("⚠️ Firebase Admin SDK non configuré correctement - Mode développement")
                    return
            
            firebase_admin.initialize_app(cred)
            print("✅ Firebase Admin SDK initialisé avec succès")
            
    except Exception as e:
        print(f"❌ Erreur initialisation Firebase Admin: {str(e)}")
        # Ne pas lever d'exception pour permettre à l'application de fonctionner
