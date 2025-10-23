from django.test import TestCase
from django.utils import timezone
from .models import Post, Tag, Comment, Reaction
from django.contrib.auth import get_user_model


class PostTestCase(TestCase):

    def setUp(self):
        # Create users (for foreign keys)
        User = get_user_model()
        self.user1 = User.objects.create(
            email='test@example.com',
            username='test_name',
            password='1234'
        )

        # Create tags
        self.tag1 = Tag.objects.create(
            name='Tag1',
            slug='tag1',
            color='#FF0000',
            description='TagDescription1'
        )
        self.tag2 = Tag.objects.create(
            name='Tag2',
            slug='tag2',
            color='#00FF00',
            description='TagDescription2'
        )

        # Create posts
        self.post1 = Post.objects.create(
            user=self.user1,
            title='Title1',
            description='Description1',
            start_time=timezone.now(),
            end_time=timezone.now())
        self.post1.tags.add(self.tag1)

        self.post2 = Post.objects.create(
            user=self.user1,
            title='Title2',
            description='Description2',
            start_time=timezone.now(),
            end_time=timezone.now())
        self.post2.tags.add(self.tag2)

    def test_get_posts(self):
        post1 = Post.objects.get(title='Title1')
        post2 = Post.objects.get(description='Description2')

        self.assertEqual(post1.description, 'Description1')
        self.assertEqual(post2.title, 'Title2')

    def test_get_tags(self):
        tag1 = Tag.objects.get(name='Tag1')
        tag2 = Tag.objects.get(slug='tag2')

        self.assertEqual(tag1.description, 'TagDescription1')
        self.assertEqual(tag2.description, 'TagDescription2')

    def test_tags_in_post(self):
        self.assertIn(self.tag1, self.post1.tags.all())
        self.assertIn(self.tag2, self.post2.tags.all())

    def test_posts_in_tags(self):
        self.assertIn(self.post1, self.tag1.posts.all())
        self.assertIn(self.post2, self.tag2.posts.all())
