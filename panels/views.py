
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Panel  # On importe ton modèle Panel
from .models import Question
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
from .models import Panel, Question, Theme, Vote # Ajoute Theme et Vote ici

@login_required
def dashboard_view(request):
    # 1. On récupère les panels avec le compte des questions totales et répondues
    user_panels = Panel.objects.filter(owner=request.user).annotate(
        questions_count=Count('questions'),
        answered_count=Count('questions', filter=Q(questions__is_answered=True))
    ).order_by('-created_at')
    
    # 2. Calcul des stats globales pour les petits cadrans du haut
    # On additionne toutes les questions de tous les panels de l'utilisateur
    total_questions = sum(p.questions_count for p in user_panels)
    
    # Simulation des participants (en attendant d'avoir un modèle Participant)
    total_participants = 0

    context = {
        'panels': user_panels,
        'total_panels': user_panels.count(),
        'total_questions': total_questions,
        'total_participants': total_participants,
    }
    
    return render(request, 'panels/admin/dashboard.html', context)


@login_required
def create_panel(request):
    if request.method == 'POST':
        # On récupère le titre tapé dans la Modal
        title = request.POST.get('title')
        
        if title:
            # On crée l'entrée dans la base de données
            # 'owner=request.user' lie automatiquement le panel à la personne connectée
            Panel.objects.create(
                title=title,
                owner=request.user,
                status='active'
            )
            
    # Une fois créé, on recharge la page du dashboard
    return redirect('dashboard')

@login_required
def panels_list_view(request):
    # Affiche uniquement la liste complète des salons
    panels = Panel.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'panels/admin/panels_list.html', {'panels': panels})

# Dans panels/views.py
@login_required
def questions_manage_view(request):
    all_q = Question.objects.filter(panel__owner=request.user)
    context = {
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
def projection_view(request):
    # On utilise 'created_at' car 'updated_at' n'existe pas dans ton modèle Question
    featured = Question.objects.filter(is_featured=True).order_by('-created_at').first()
    return render(request, 'panels/admin/projection.html', {'featured_question': featured})

# Vue pour les Votes
def votes_view(request):
    top_q = Question.objects.all().order_by('-created_at')[:5]
    return render(request, 'panels/admin/votes.html', {'top_questions': top_q})

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
            # Redirige vers la page de thèmes pour ce panel (sans exiger d'argument dans l'URL)
            return redirect('themes')



    # 3. LOGIQUE D'AFFICHAGE
    themes_list = list(Theme.objects.filter(panel=panel, is_active=True))
    total_votes = Vote.objects.filter(theme__panel=panel).count()
    
    for theme in themes_list:
        count = theme.votes.count()
        theme.vote_count = count
        theme.percentage = round((count / total_votes) * 100) if total_votes > 0 else 0
            
    themes_sorted = sorted(themes_list, key=lambda x: x.vote_count, reverse=True)
            
    context = {
        'panel': panel, # Important pour le template !
        'themes': themes_sorted,
        'total_votes': total_votes,
        'winning_theme': themes_sorted[0] if total_votes > 0 and themes_sorted else None
    }
    return render(request, 'panels/admin/themes.html', context)

def public_index(request):
    themes = Theme.objects.filter(is_active=True).order_by('order')
    return render(request, 'panels/public/index.html', {'themes': themes})

def submit_question(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        
        # On récupère le premier panel par défaut pour le moment
        panel = Panel.objects.first()
        
        new_q = Question.objects.create(
            panel=panel,
            text=data.get('text'),
            author_name=data.get('author', 'Anonyme'),
            is_approved=True # On peut changer ça pour modération manuelle
        )
        
        return JsonResponse({"status": "success", "id": new_q.id})
    return JsonResponse({"status": "error"}, status=400)


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
        
    return render(request, 'panels/admin/settings.html', {'panel': panel})

def delete_panel(request, panel_id):
    if request.method == "POST":
        # On ajoute owner=request.user pour être sûr que c'est bien son panel !
        panel = get_object_or_404(Panel, id=panel_id, owner=request.user)
        panel.delete()
    return redirect('dashboard')

def panel_view(request, unique_id):
    panel = get_object_or_404(Panel, unique_id=unique_id)
    return render(request, 'panels/live_view.html', {'panel': panel})

@login_required
def delete_theme(request, theme_id):
    theme = get_object_or_404(Theme, id=theme_id, panel__owner=request.user)
    panel_id = theme.panel.id
    theme.delete()
    return redirect('themes', panel_id=panel_id)