
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import json
import logging
import os
from firebase_admin import auth as firebase_auth
from .firebase_init import initialize_firebase

initialize_firebase()

logger = logging.getLogger(__name__)

def get_firebase_config():
    """Retourne la configuration Firebase depuis les variables d'environnement"""
    return {
        'apiKey': os.getenv('FIREBASE_API_KEY', 'AIzaSyCbaAEonMkoqsUMDCvV7xWPdbL5jY9p1gE'),
        'authDomain': os.getenv('FIREBASE_AUTH_DOMAIN', 'qroom-bb7db.firebaseapp.com'),
        'projectId': os.getenv('FIREBASE_PROJECT_ID', 'qroom-bb7db'),
        'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET', 'qroom-bb7db.firebasestorage.app'),
        'messagingSenderId': os.getenv('FIREBASE_MESSAGING_SENDER_ID', '113139462472'),
        'appId': os.getenv('FIREBASE_APP_ID', '1:113139462472:web:416ddd12726e21605f837d'),
        'measurementId': os.getenv('FIREBASE_MEASUREMENT_ID', 'G-Y58Z4PJM6F')
    }

def register_view(request):
    if request.method == 'POST':
        u_name = request.POST.get('username')
        u_email = request.POST.get('email')
        u_pass = request.POST.get('password')

        try:
            # Vérifier si l'utilisateur existe déjà
            if User.objects.filter(username=u_name).exists():
                messages.error(request, "Ce nom d'utilisateur est déjà pris.")
                return render(request, 'accounts/register.html')
            
            user = User.objects.create_user(username=u_name, email=u_email, password=u_pass)
            auth_login(request, user) 
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f"Erreur : {e}")
            
    return render(request, 'accounts/register.html', {
        'firebase_config': get_firebase_config()
    })

def login_view(request):
    if request.method == 'POST':
        email_saisi = request.POST.get('username') # On récupère ce qui est tapé
        u_pass = request.POST.get('password')

        try:
            # On cherche l'utilisateur qui a cet email en base de données
            user_found = User.objects.get(email=email_saisi)
            # On utilise son 'username' réel pour l'authentification Django
            user = authenticate(request, username=user_found.username, password=u_pass)
            
            if user is not None:
                auth_login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "Mot de passe incorrect.")
        except User.DoesNotExist:
            messages.error(request, "Aucun compte trouvé avec cet email.")
            
    return render(request, 'accounts/login.html', {
        'firebase_config': get_firebase_config()
    })

def logout_view(request):
    logout(request)
    return redirect('login')


# ==================== FIREBASE AUTHENTICATION ====================

@csrf_exempt
@require_http_methods(["POST"])
def firebase_login(request):
    try:
        data = json.loads(request.body)
        id_token = data.get('idToken')  # ← Token envoyé par le frontend
        
        print(f"DEBUG: id_token reçu = {id_token[:50]}..." if id_token else "DEBUG: id_token = None")

        if not id_token:
            return JsonResponse({'error': 'Token manquant'}, status=400)

        # ✅ Vérification sécurisée
        decoded_token = firebase_auth.verify_id_token(id_token)
        email = decoded_token.get('email')
        firebase_uid = decoded_token.get('uid')
        display_name = decoded_token.get('name', email.split('@')[0])
        photo_url = decoded_token.get('picture', '')
        
        print(f"DEBUG: Utilisateur Firebase = {email}, UID = {firebase_uid}")

        if not email:
            return JsonResponse({'error': 'Email manquant dans le token'}, status=400)

        # Récupérer ou créer l'utilisateur Django
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email.split('@')[0],
                'first_name': display_name.split()[0] if display_name else '',
                'last_name': ' '.join(display_name.split()[1:]) if len(display_name.split()) > 1 else '',
            }
        )
        
        print(f"DEBUG: User Django {'créé' if created else 'existant'} = {user.username} (ID: {user.id})")

        auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        print(f"DEBUG: Utilisateur connecté avec succès")

        return JsonResponse({'success': True, 'created': created})

    except firebase_auth.InvalidIdTokenError as e:
        print(f"DEBUG: Token Firebase invalide = {str(e)}")
        return JsonResponse({'error': 'Token Firebase invalide'}, status=401)
    except Exception as e:
        print(f"DEBUG: Erreur Firebase login = {str(e)}")
        logger.error(f"Erreur Firebase login: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def firebase_register(request):
    try:
        data = json.loads(request.body)
        id_token = data.get('idToken')  # ← Token envoyé par le frontend
        
        print(f"DEBUG REGISTER: id_token reçu = {id_token[:50]}..." if id_token else "DEBUG REGISTER: id_token = None")

        if not id_token:
            return JsonResponse({'error': 'Token manquant'}, status=400)

        # ✅ Vérification sécurisée
        decoded_token = firebase_auth.verify_id_token(id_token)
        email = decoded_token.get('email')
        firebase_uid = decoded_token.get('uid')
        display_name = decoded_token.get('name', email.split('@')[0])
        photo_url = decoded_token.get('picture', '')
        
        print(f"DEBUG REGISTER: Utilisateur Firebase = {email}, UID = {firebase_uid}")

        if not email:
            return JsonResponse({'error': 'Email manquant dans le token'}, status=400)

        # Vérifier si l'utilisateur existe déjà
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email.split('@')[0],
                'first_name': display_name.split()[0] if display_name else '',
                'last_name': ' '.join(display_name.split()[1:]) if len(display_name.split()) > 1 else '',
            }
        )

        # Si l'utilisateur existe déjà mais avec un username en conflit, générer un username unique
        if not created:
            base_username = email.split('@')[0]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exclude(id=user.id).exists():
                username = f"{base_username}{counter}"
                counter += 1
            user.username = username
            user.save()

        print(f"DEBUG REGISTER: User Django {'créé' if created else 'existant'} = {user.username} (ID: {user.id})")

        auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        print(f"DEBUG REGISTER: Utilisateur connecté avec succès")

        return JsonResponse({'success': True, 'created': created})

    except firebase_auth.InvalidIdTokenError as e:
        print(f"DEBUG REGISTER: Token Firebase invalide = {str(e)}")
        return JsonResponse({'error': 'Token Firebase invalide'}, status=401)
    except Exception as e:
        print(f"DEBUG REGISTER: Erreur Firebase register = {str(e)}")
        logger.error(f"Erreur Firebase register: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
