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
from django.conf import settings
from django.conf.urls.static import static
from core.views import landing
from django.http import HttpResponse
from accounts.views import login_view, register_view, logout_view, firebase_login, firebase_register
from panels.views import dashboard_view, create_panel, toggle_question_status
from panels import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing, name='landing'),
    path('dashboard/', dashboard_view, name='dashboard'),

    # Authentification
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    
    # Firebase Authentication
    path('api/auth/firebase-login/', firebase_login, name='firebase_login'),
    path('api/auth/firebase-register/', firebase_register, name='firebase_register'),

    # Gestion d'un Panel spécifique (C'est ceux-là que ta sidebar utilise)
    path('create-panel/', create_panel, name='create_panel'),
    path('panel/<int:panel_id>/questions/', views.questions_manage_view, name='panel_questions'),
    path('panel/<int:panel_id>/themes/', views.themes_view, name='panel_themes'),
    path('panel/<int:panel_id>/projection/', views.projection_view, name='panel_projection'),
    path('panel/<int:panel_id>/settings/', views.panel_settings, name='panel_settings'),
    path('delete-panel/<int:panel_id>/', views.delete_panel, name='delete_panel'),

    # Routes adicionales
    path('theme/delete/<int:theme_id>/', views.delete_theme, name='delete_theme'),

    # Questions/Voting
    path('question/<int:q_id>/action/', views.toggle_question_status, name='question_action'),
    path('toggle-question/<int:q_id>/', views.toggle_question_status, name='toggle_question_status'),
    path('vote/<int:theme_id>/', views.cast_vote_ajax, name='cast_vote'),

    # Public
    path('p/', views.public_index, name='public_index'),
    path('p/<uuid:unique_id>/', views.public_panel_view, name='public_view'),

    # API
    path('api/submit-question/', views.submit_question, name='submit_question'),
]

# Servir les fichiers statiques et médias en développement
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
