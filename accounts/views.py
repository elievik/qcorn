
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging

logger = logging.getLogger(__name__)

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
            
    return render(request, 'accounts/register.html')

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
            
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')


# ==================== FIREBASE AUTHENTICATION ====================

@csrf_exempt
@require_http_methods(["POST"])
def firebase_login(request):
    """
    Vue pour gérer la connexion/inscription via Firebase
    Reçoit l'ID token Firebase du client et crée/synchronise l'utilisateur Django
    """
    try:
        data = json.loads(request.body)
        firebase_uid = data.get('uid')
        email = data.get('email')
        display_name = data.get('displayName', email.split('@')[0])
        photo_url = data.get('photoURL')
        
        if not firebase_uid or not email:
            return JsonResponse({'error': 'Données manquantes'}, status=400)
        
        # Récupérer ou créer l'utilisateur Django
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email.split('@')[0],
                'first_name': display_name.split()[0] if display_name else '',
                'last_name': ' '.join(display_name.split()[1:]) if len(display_name.split()) > 1 else '',
            }
        )
        
        if not created:
            # Mettre à jour le nom si c'est différent
            user.first_name = display_name.split()[0] if display_name else ''
            user.last_name = ' '.join(display_name.split()[1:]) if len(display_name.split()) > 1 else ''
            user.save()
        
        # Connecter l'utilisateur
        auth_login(request, user)
        
        return JsonResponse({
            'success': True,
            'message': 'Connexion réussie',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'display_name': user.get_full_name() or user.username
            }
        })
        
    except Exception as e:
        logger.error(f"Erreur Firebase login: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def firebase_register(request):
    """
    Vue pour gérer l'inscription via Firebase avec données personnalisées
    """
    try:
        data = json.loads(request.body)
        firebase_uid = data.get('uid')
        email = data.get('email')
        display_name = data.get('displayName', '')
        photo_url = data.get('photoURL', '')
        
        if not firebase_uid or not email:
            return JsonResponse({'error': 'Données manquantes'}, status=400)
        
        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Un compte avec cet email existe déjà'}, status=400)
        
        # Créer l'utilisateur Django
        username = email.split('@')[0]
        # Assurer l'unicité du username
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=display_name.split()[0] if display_name else '',
            last_name=' '.join(display_name.split()[1:]) if len(display_name.split()) > 1 else '',
        )
        
        # Connecter l'utilisateur
        auth_login(request, user)
        
        return JsonResponse({
            'success': True,
            'message': 'Inscription réussie',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'display_name': user.get_full_name() or user.username
            }
        })
        
    except Exception as e:
        logger.error(f"Erreur Firebase register: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
