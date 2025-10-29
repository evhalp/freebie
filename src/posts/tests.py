from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import IntegrityError
from datetime import timedelta
from posts.models import Post, Tag, Reaction, Comment

class TagModelTest(TestCase):

    def setUp(self):
        self.tag = Tag.objects.create(
            name='Test Name',
            slug='test_name',
            description='Test Description',
            bg_color='#000000',
            text_color='#FFFFFF'
        )

    def test_tag_creation(self):
        self.assertEqual(self.tag.name, 'Test Name')
        self.assertEqual(self.tag.slug, 'test_name')
        self.assertEqual(self.tag.description, 'Test Description')
        self.assertEqual(self.tag.bg_color, '#000000')
        self.assertEqual(self.tag.text_color, '#FFFFFF')

class PostModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.tag_1 = Tag.objects.create(
            name='Test Tag 1',
            slug='test_tag_1',
            description='Test Tag Description 1',
        )
        self.tag_2 = Tag.objects.create(
            name='Test Tag 2',
            slug='test_tag_2',
            description='Test Tag Description 2',
        )
        self.post = Post.objects.create(
            user=self.user,
            title='Test Post',
            description='Test Description',
            location='Test Location',
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=2)
        )
        self.post.tags.add(self.tag_1, self.tag_2)

    def test_post_creation(self):
        self.assertEqual(self.post.user, self.user)
        self.assertEqual(self.post.title, 'Test Post')
        self.assertEqual(self.post.description, 'Test Description')
        self.assertEqual(self.post.location, 'Test Location')

    def test_post_default_img(self):
        self.assertEqual(self.post.image, 'default.png')

    def test_post_tags(self):
        self.assertEqual(self.tag_1, self.post.tags.first())
        self.assertEqual(self.tag_2, self.post.tags.last())

class CommentModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.post = Post.objects.create(
            user=self.user,
            title='Test Post',
            description='Test Description',
            location='Test Location',
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=2)
        )
        self.comment_1 = Comment.objects.create(
            post=self.post,
            user=self.user,
            content='Test Comment'
        )
        self.comment_2 = Comment.objects.create(
            post=self.post,
            user=self.user,
            content='Test Nested Comment',
            parent=self.comment_1
        )

    def test_comment_creation(self):
        self.assertEqual(self.comment_1.content, 'Test Comment')
        self.assertEqual(self.comment_1.post, self.post)
        self.assertEqual(self.comment_1.user, self.user)

    def test_nested_comment(self):
        self.assertEqual(self.comment_2.content, 'Test Nested Comment')
        self.assertEqual(self.comment_2.post, self.post)
        self.assertEqual(self.comment_2.user, self.user)
        self.assertEqual(self.comment_2.parent, self.comment_1)
        self.assertIn(self.comment_2, self.comment_1.replies.all())

class ReactionModelTest(TestCase):

    def setUp(self):
        self.user_1 = User.objects.create_user(
            username='testuser1',
            password='testpassword1'
        )
        self.user_2 = User.objects.create_user(
            username='testuser2',
            password='testpassword2'
        )
        self.post = Post.objects.create(
            user=self.user_1,
            title='Test Post',
            description='Test Description',
            location='Test Location',
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=2)
        )
        self.reaction_1 = Reaction.objects.create(
            post=self.post,
            user=self.user_1,
            sentiment='LIKE',
            is_attending=True
        )
        self.reaction_2 = Reaction.objects.create(
            post=self.post,
            user=self.user_2,
            sentiment='DISLIKE',
            is_attending=False
        )

    def test_reaction_creation(self):
        self.assertEqual(self.reaction_1.sentiment, 'LIKE')
        self.assertEqual(self.reaction_2.sentiment, 'DISLIKE')
        self.assertTrue(self.reaction_1.is_attending)
        self.assertFalse(self.reaction_2.is_attending)

    def test_reaction_unique(self):
        with self.assertRaises(IntegrityError):
            Reaction.objects.create(
                post=self.post,
                user=self.user_1,
                sentiment='DISLIKE'
            )
