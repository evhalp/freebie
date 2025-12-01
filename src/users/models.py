from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default-profile.png', upload_to='post/images', blank=True)
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
    
    def follow(self, user_profile):
        """Follow another UserProfile and adjust their credibility."""
        if user_profile != self:
            self.following.add(user_profile)
            try:
                from users.weights import adjust_credibility, W_FOLLOW
                adjust_credibility(user_profile.user, W_FOLLOW)
            except Exception:
                # don't let credibility update failures block following
                pass

    def unfollow(self, user_profile):
        """Unfollow another UserProfile and decrement their credibility."""
        self.following.remove(user_profile)
        try:
            from users.weights import adjust_credibility, W_FOLLOW
            adjust_credibility(user_profile.user, -W_FOLLOW)
        except Exception:
            pass

    def is_following(self, user):
        return self.following.filter(pk=user.pk).exists()
