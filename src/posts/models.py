from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255, blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    image_path = models.CharField(max_length=500, blank=True, null=True)
    # Django could also handle image uploads with models.ImageField(upload_to='posts/', blank=True, null=True), if we prefer
    # We'd need to pip install pillow, first, though
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'"{self.title}" by {self.user.username}'