"""
URL configuration for qcorn project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from core.views import landing
from django.http import HttpResponse
from accounts.views import login_view, register_view # Importe tes nouvelles vues
from panels.views import dashboard_view, create_panel, toggle_question_status
from panels import views
from accounts.views import logout_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing, name='landing'),

    # Utilise les vraies vues d'authentification
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    # On garde juste un petit placeholder pour le dashboard le temps de le créer
    path('create-panel/', lambda r: HttpResponse("<h1>Succès !</h1><p>Panel créé avec succès.</p>"), name='create-panel'),path('dashboard/', dashboard_view, name='dashboard'),
    path('dashboard/create/', create_panel, name='create_panel'),
    path('question/<int:q_id>/action/', views.toggle_question_status, name='question_action'),
    path('dashboard/questions/', views.questions_manage_view, name='questions_manage'),
    path('dashboard/questions/', views.questions_manage_view, name='questions_manage'),
    path('dashboard/themes/', views.themes_view, name='themes'),
    path('dashboard/projection/', views.projection_view, name='projection'),
    path('logout/', logout_view, name='logout'),

    path('api/submit-question/', views.submit_question, name='submit_question'),
    path('p/', views.public_index, name='public_index'), # La page que les gens verront
    path('panel/<int:panel_id>/settings/', views.panel_settings, name='panel_settings'),
    path('p/<uuid:unique_id>/', views.public_panel_view, name='public_view'),
    path('delete-panel/<int:panel_id>/', views.delete_panel, name='delete_panel'),
    path('panel/<int:panel_id>/themes/', views.themes_view, name='themes'),
    path('theme/delete/<int:theme_id>/', views.delete_theme, name='delete_theme'),
    path('vote/<int:theme_id>/', views.cast_vote_ajax, name='cast_vote'),
    path('toggle-question/<int:q_id>/', views.toggle_question_status, name='toggle_question_status'),
]
