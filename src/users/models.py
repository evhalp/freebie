from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.png', upload_to='post/images', blank=True)
    bio = models.TextField(blank=True)
    credibility = models.IntegerField(default=0)
    following = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='followers',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

    def get_credibility(self):
        return self.credibility
    
    def follow(self, user):
        if user != self:
            self.following.add(user)

    def unfollow(self, user):
        self.following.remove(user)

    def is_following(self, user):
        return self.following.filter(pk=user.pk).exists()
