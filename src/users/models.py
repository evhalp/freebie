from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    credibility = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

    def get_credibility(self):
        return self.credibility
