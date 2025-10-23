from django.test import TestCase
from django.utils import timezone
from .models import Post, Tag, Comment, Reaction
from django.contrib.auth import get_user_model
class PostTestCase(TestCase):

    def setUp(self):
        # Create users (for foreign keys)
        User = get_user_model()
        user1 = User.objects.create(
            email='test@example.com',
            username='test_name',
            password='1234'
        )

        # Create tags
        tag1 = Tag.objects.create(
            name='Tag1',
            color='#FF0000',
            description='TagDescription1'
        )
        tag2 = Tag.objects.create(
            name='Tag2',
            color='#00FF00',
            description='TagDescription2'
        )

        # Create posts
        post1 = Post.objects.create(
            user=user1,
            title='Title1',
            description='Description1',
            start_time=timezone.now(),
            end_time=timezone.now())
        post2 = Post.objects.create(
            user=user1,
            title='Title2',
            description='Description2',
            start_time=timezone.now(),
            end_time=timezone.now())

    def test_get_posts(self):
        post1 = Post.objects.get(title='Title1')
        post2 = Post.objects.get(title='Title2')
        self.assertEqual(post1.description, 'Description1')
        self.assertEqual(post2.description, 'Description2')




