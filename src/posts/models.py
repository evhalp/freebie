from django.db import models
from django.contrib.auth.models import User

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField()
    color = models.CharField(max_length=7, default='#000000')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.slug})'

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
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    image_path = models.CharField(max_length=500, blank=True, null=True)
    # Django could also handle image uploads with models.ImageField(upload_to='posts/', blank=True, null=True), if we prefer
    # We'd need to pip install pillow, first, though
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'"{self.title}" by {self.user.username}'
    
class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField()
    parent = models.ForeignKey(  # For nested comments (replies to other comments)
        'self',
        on_delete=models.CASCADE,
        related_name='replies',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.user.username} on "{self.post.title}"'

class PostReaction(models.Model):
    REACTION_CHOICES = [
        ('LIKE', 'Like'),
        ('DISLIKE', 'Dislike'),
        ('GOING', 'Going'),
    ]

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='reactions'
    )
    user = models.ForeignKey(
        User,
    )