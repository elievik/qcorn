import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def initialize_firebase():
    """
    Initialise Firebase Admin SDK avec les variables d'environnement.
    Désactivé en production pour éviter les erreurs.
    """
    try:
        # Firebase désactivé pour éviter les erreurs en production
        logger.warning("Firebase désactivé en production - Mode développement")
        return
            
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de Firebase: {e}")
        return
