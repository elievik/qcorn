
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Panel  # On importe ton modèle Panel
from .models import Question
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

@login_required
def dashboard_view(request):
    # 1. On récupère tous les panels qui appartiennent à l'utilisateur connecté
    # On les trie du plus récent au plus ancien
    user_panels = Panel.objects.filter(owner=request.user).order_by('-created_at')
    
    # 2. On prépare les données pour les statistiques du dashboard
    context = {
        'panels': user_panels,
        'total_panels': user_panels.count(),
        # Pour l'instant on met 0 pour les questions/participants, on les liera plus tard
        'total_questions': 0,
        'total_participants': 0,
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
    featured = Question.objects.filter(is_featured=True).order_by('-created_at').first()
    return render(request, 'panels/admin/projection.html', {'featured_question': featured})

# Vue pour les Votes
def votes_view(request):
    top_q = Question.objects.all().order_by('-created_at')[:5]
    return render(request, 'panels/admin/votes.html', {'top_questions': top_q})

# Vue pour les Thèmes (Celle qui causait l'erreur)
def themes_view(request):
    return render(request, 'panels/admin/themes.html')


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