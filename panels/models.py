from django.db import models

from django.db import models
from django.contrib.auth.models import User
import uuid

class Panel(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Terminé'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="panels")
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True) # Pour l'URL genre qroom.io/p/mon-event
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return self.title

# Ajoute ceci à la suite de ton modèle Panel dans panels/models.py
class Question(models.Model):
    panel = models.ForeignKey(Panel, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    author_name = models.CharField(max_length=100, default="Anonyme")
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)
    is_answered = models.BooleanField(default=False)
    # AJOUTE CETTE LIGNE :
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.author_name}: {self.text[:30]}"

class Vote(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="votes")
    # On utilise l'ID de session pour éviter qu'une personne vote 100 fois
    session_key = models.CharField(max_length=100)

    class Meta:
        unique_together = ('question', 'session_key') # Un vote par personne par question


# panels/models.py
from django.db import models

class Theme(models.Model):
    title = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    def __clic_count(self):
        return self.votes.count()

    def __str__(self):
        return self.title

class Vote(models.Model):
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name="votes")
    user_session = models.CharField(max_length=255) # Pour éviter qu'une personne vote 100 fois
    created_at = models.DateTimeField(auto_now_add=True)