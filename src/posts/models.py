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
    image = models.ImageField(default='default.png', upload_to='post/images', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.pk and not self.image:
            self.image = self.image.field.default
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'"{self.title}" by {self.user.username}'
    
    def get_like_count(self):
        return self.reactions.filter(sentiment='LIKE').count()
    
    def get_dislike_count(self):
        return self.reactions.filter(sentiment='DISLIKE').count()

    def get_attendance(self):
        return self.reactions.filter(is_attending=True).count()

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

class Reaction(models.Model):
    SENTIMENT_ENUM = [
        ('LIKE', 'Liked'),
        ('DISLIKE', 'Disliked')
    ]

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='reactions'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reactions'
    )
    sentiment = models.CharField(
        max_length=10,
        choices=SENTIMENT_ENUM,
        blank=True,
        null=True
    )
    is_attending = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['post', 'user']
        ordering = ['-created_at']

    def __str__(self):
        reactions = []
        if self.sentiment:
            reactions.append(self.sentiment)
        if self.is_attending:
            reactions.append("is attending")
        reaction_str = " and ".join(reactions) if reactions else "No reactions"
        return f'{self.user.username} {reaction_str} "{self.post.title}"'
    