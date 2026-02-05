
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages

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

from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return redirect('login')