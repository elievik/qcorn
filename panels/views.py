from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Panel  # On importe ton modèle Panel
from .models import Question
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
from .models import Panel, Question, Theme, Vote # Ajoute Theme et Vote ici
import qrcode
import io
import base64
from django.urls import reverse
from django.contrib import messages


@login_required
def dashboard_view(request):
    try:
        user_panels = Panel.objects.filter(owner=request.user).annotate(
            questions_count=Count('questions'),
            answered_count=Count('questions', filter=Q(questions__is_answered=True))
        ).order_by('-created_at')
        
        # Correction : Génération du lien UUID et du QR Code
        for panel in user_panels:
            try:
                # On s'assure que l'URL utilise l'hôte actuel (ex: 127.0.0.1:8000)
                public_url = request.build_absolute_uri(reverse('public_view', args=[panel.unique_id]))
                panel.public_url = public_url
                
                # Génération du QR Code
                qr = qrcode.QRCode(version=1, box_size=5, border=2)
                qr.add_data(public_url)
                qr.make(fit=True)
                
                # IMPORTANT : On force le format RGB pour éviter les erreurs d'affichage
                img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
                
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                panel.qr_code = base64.b64encode(buffer.getvalue()).decode()
            except Exception as e:
                panel.qr_code = None  # Fallback
        
        context = {
            'panels': user_panels,
            'total_panels': user_panels.count(),
            'total_questions': sum(p.questions_count for p in user_panels),
            'total_participants': 0,
        }
        return render(request, 'panels/admin/dashboard.html', context)
    
    except Exception as e:
        messages.error(request, f'Erreur lors du chargement du dashboard: {str(e)}')
        # Retourner un dashboard vide en cas d'erreur
        context = {
            'panels': [],
            'total_panels': 0,
            'total_questions': 0,
            'total_participants': 0,
        }
        return render(request, 'panels/admin/dashboard.html', context)

@login_required
def create_panel(request):
    if request.method == 'POST':
        try:
            # On récupère le titre tapé dans la Modal
            title = request.POST.get('title')
            
            if not title or not title.strip():
                messages.error(request, 'Le titre du panel ne peut pas être vide.')
                return redirect('dashboard')
            
            # On crée l'entrée dans la base de données
            # 'owner=request.user' lie automatiquement le panel à la personne connectée
            panel = Panel.objects.create(
                title=title.strip(),
                owner=request.user,
                status='active'
            )
            
            messages.success(request, f'Panel "{panel.title}" créé avec succès!')
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la création du panel: {str(e)}')
            
    # Une fois créé, on recharge la page du dashboard
    return redirect('dashboard')

@login_required
def panels_list_view(request):
    # Affiche uniquement la liste complète des salons
    panels = Panel.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'panels/admin/panels_list.html', {'panels': panels})

# Dans panels/views.py
# Dans panels/views.py
@login_required
def questions_manage_view(request, panel_id=None):
    # Le panel_id doit toujours être fourni via l'URL
    if panel_id:
        all_q = Question.objects.filter(panel_id=panel_id, panel__owner=request.user)
    else:
        # Fallback : si pas de panel_id, on prend le premier panel de l'utilisateur
        first_panel = Panel.objects.filter(owner=request.user).first()
        if not first_panel:
            return redirect('dashboard')
        all_q = Question.objects.filter(panel=first_panel)
    
    context = {
        'panels': Panel.objects.filter(owner=request.user).order_by('-created_at'),
        'questions': all_q.order_by('-created_at'),
        'count_new': all_q.filter(is_answered=False).count(),
        'count_answered': all_q.filter(is_answered=True).count(),
        'count_featured': all_q.filter(is_featured=True).count(),
    }
    return render(request, 'panels/admin/questions.html', context)

@login_required
def toggle_question_status(request, q_id):
    # On récupère la question (seulement si elle appartient à un panel de l'admin)
    question = get_object_or_404(Question, id=q_id, panel__owner=request.user)
    
    action = request.GET.get('action')
    
    if action == 'approve':
        question.is_answered = True
    elif action == 'delete':
        question.delete()
        return JsonResponse({'status': 'deleted'})
    elif action == 'star':
        question.is_featured = not question.is_featured
    
    question.save()
    return JsonResponse({'status': 'updated'})


# Vue pour la Projection
@login_required
def projection_view(request, panel_id):
    # 1. On récupère le panel spécifique grâce à son ID
    panel = get_object_or_404(Panel, id=panel_id, owner=request.user)
    
    # 2. On récupère la question mise en avant uniquement pour CE panel
    featured = Question.objects.filter(
        panel=panel,
        is_featured=True
    ).order_by('-created_at').first()
    
    # 3. On envoie les deux à la page HTML
    return render(request, 'panels/admin/projection.html', {
        'panels': Panel.objects.filter(owner=request.user).order_by('-created_at'),
        'featured_question': featured,
        'panel': panel
    })
# Vue pour les Votes
@login_required
def votes_view(request):
    # Récupérer le premier panel pour afficher les votes associés
    first_panel = Panel.objects.filter(owner=request.user).first()
    if first_panel:
        top_q = Question.objects.filter(panel=first_panel).order_by('-created_at')[:10]
    else:
        top_q = Question.objects.none()
    
    return render(request, 'panels/admin/votes.html', {
        'panels': Panel.objects.filter(owner=request.user).order_by('-created_at'),
        'top_questions': top_q
    })

# Vue pour les Thèmes (Celle qui causait l'erreur)
@login_required
def themes_view(request, panel_id=None):
    # Si l'ID du panel n'est pas fourni, on essaie de le récupérer depuis le POST
    # (le formulaire fournit désormais `panel_id`) ou on prend le premier panel
    if panel_id is None:
        # Priorité au panel envoyé via POST
        panel_id = request.POST.get('panel_id') or request.GET.get('panel_id')

    if panel_id:
        panel = get_object_or_404(Panel, id=panel_id, owner=request.user)
    else:
        # Si l'utilisateur n'a aucun panel, rediriger vers le dashboard
        first_panel = Panel.objects.filter(owner=request.user).order_by('-created_at').first()
        if not first_panel:
            return redirect('dashboard')
        panel = first_panel

    # 2. LOGIQUE DE CRÉATION (Traitement du formulaire)
    if request.method == "POST":
        title = request.POST.get('title')
        if title:
            Theme.objects.create(
                panel=panel,
                title=title,
                is_active=True
            )
            # Redirige vers la page de thèmes pour ce panel
            return redirect('panel_themes', panel_id=panel.id)



    # 3. LOGIQUE D'AFFICHAGE
    themes_list = list(Theme.objects.filter(panel=panel, is_active=True))
    total_votes = Vote.objects.filter(theme__panel=panel).count()
    
    for theme in themes_list:
        count = theme.votes.count()
        theme.vote_count = count
        theme.percentage = round((count / total_votes) * 100) if total_votes > 0 else 0
            
    themes_sorted = sorted(themes_list, key=lambda x: x.vote_count, reverse=True)
            
    context = {
        'panels': Panel.objects.filter(owner=request.user).order_by('-created_at'),
        'panel': panel, # Important pour le template !
        'themes': themes_sorted,
        'total_votes': total_votes,
        'winning_theme': themes_sorted[0] if total_votes > 0 and themes_sorted else None
    }
    return render(request, 'panels/admin/themes.html', context)

def public_index(request):
    # Page d'accueil publique - redirige vers le dashboard ou affiche un message
    return redirect('landing')

def submit_question(request):
    # Cette fonction ne doit plus être utilisée - les questions vont via public_panel_view
    return JsonResponse({"status": "error", "message": "Utilisez le formulaire public"}, status=400)


from django.utils import timezone

def panel_settings(request, panel_id):
    panel = get_object_or_404(Panel, id=panel_id, owner=request.user)
    
    if request.method == "POST":
        panel.title = request.POST.get('title')
        panel.status = request.POST.get('status')
        
        # Gestion de la programmation
        start_dt = request.POST.get('scheduled_start')
        if start_dt:
            panel.scheduled_start = start_dt
            
        panel.duration_minutes = request.POST.get('duration')
        panel.auto_close = 'auto_close' in request.POST
        
        panel.save()
        return redirect('dashboard')
        
    # Redirection si l'utilisateur accède directement à cette URL
    # Les paramètres se gèrent via le modal dans le dashboard
    return redirect('dashboard')

def delete_panel(request, panel_id):
    if request.method == "POST":
        # On ajoute owner=request.user pour être sûr que c'est bien son panel !
        panel = get_object_or_404(Panel, id=panel_id, owner=request.user)
        panel.delete()
    return redirect('dashboard')

def panel_view(request, unique_id):
    # Fonction obsolète - utilisée publiquement
    panel = get_object_or_404(Panel, unique_id=unique_id)
    themes = panel.themes.filter(is_active=True)
    return render(request, 'panels/public/live.html', {'panel': panel, 'themes': themes})

@login_required
def delete_theme(request, theme_id):
    theme = get_object_or_404(Theme, id=theme_id, panel__owner=request.user)
    panel_id = theme.panel.id
    theme.delete()
    return redirect('panel_themes', panel_id=panel_id)


# Change panel_id par unique_id
def public_panel_view(request, unique_id):
    # On cherche par unique_id (UUID) pour plus de sécurité
    panel = get_object_or_404(Panel, unique_id=unique_id)
    
    # Vérifier que le panel est actif
    if panel.status != 'active':
        return render(request, 'panels/public/waiting_room.html', {'panel': panel})
    
    themes = panel.themes.filter(is_active=True)
    
    if request.method == "POST":
        author = request.POST.get('author_name', 'Anonyme').strip() or 'Anonyme'
        text = request.POST.get('question_text', '').strip()
        if text:
            Question.objects.create(panel=panel, author_name=author, text=text)
            # On redirige vers l'UUID
            return redirect('public_view', unique_id=panel.unique_id)

    context = {
        'panel': panel,
        'themes': themes,
        'total_votes': Vote.objects.filter(theme__panel=panel).count()
    }
    return render(request, 'panels/public/live.html', context)


def cast_vote_ajax(request, theme_id):
    # Vérifier que le thème existe et qu'il est actif
    theme = get_object_or_404(Theme, id=theme_id, is_active=True)
    # Vérifier que le panel est actif
    if theme.panel.status != 'active':
        return JsonResponse({'status': 'error', 'message': 'Le panel n\'est pas actif'}, status=400)
    Vote.objects.create(theme=theme)
    return JsonResponse({'status': 'ok'})

@login_required
def toggle_question_status(request, q_id):
    question = get_object_or_404(Question, id=q_id, panel__owner=request.user)
    action = request.GET.get('action')
    
    if action == 'approve':
        question.is_answered = True
    elif action == 'star':
        question.is_featured = not question.is_featured
    elif action == 'delete':
        question.delete()
        return JsonResponse({'status': 'deleted'})
    
    question.save()
    return JsonResponse({'status': 'updated'})

