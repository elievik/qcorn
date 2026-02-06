import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

class Panel(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Terminé'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="panels")
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    is_public = models.BooleanField(default=True)
    
    # Programmation
    scheduled_start = models.DateTimeField(null=True, blank=True) 
    duration_minutes = models.PositiveIntegerField(null=True, blank=True, help_text="Durée en minutes")
    auto_close = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    

    @property
    def is_expired(self):
        if self.scheduled_start and self.duration_minutes:
            end_time = self.scheduled_start + timezone.timedelta(minutes=self.duration_minutes)
            return timezone.now() > end_time
        return False

class Question(models.Model):
    panel = models.ForeignKey(Panel, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    author_name = models.CharField(max_length=100, default="Anonyme")
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)
    is_answered = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.author_name}: {self.text[:30]}"

class Theme(models.Model):
    # On ajoute ce lien indispensable
    panel = models.ForeignKey(Panel, on_delete=models.CASCADE, related_name="themes", null=True)
    title = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.panel.title if self.panel else 'Global'} - {self.title}"

    @property
    def click_count(self):
        return self.votes.count()

class Vote(models.Model):
    # Un vote est lié à un thème ET à une session utilisateur
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name="votes")
    user_session = models.CharField(max_length=255, null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Vote pour {self.theme.title}"

def get_public_url(self, request):
        # Génère l'URL absolue (ex: http://127.0.0.1:8000/live/5/)
        path = reverse('public_view', kwargs={'panel_id': self.id})
        return request.build_absolute_uri(path)

