from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from posts.models import Post, Tag, Reaction, Comment

class SearchViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('search')

        # Test Users
        self.user_1 = User.objects.create_user(
            username='testuser1',
            password='testpassword1'
        )
        self.user_2 = User.objects.create_user(
            username='testuser2',
            password='testpassword2'
        )
        
        # Test Tags
        self.tag_1 = Tag.objects.create(
            name='Test Tag 1',
            slug='test_tag_1',
            description='Test Tag Description 1'
        )
        self.tag_2 = Tag.objects.create(
            name='Test Tag 2',
            slug='test_tag_2',
            description='Test Tag Description 2'
        )

        # Test Posts

        now = timezone.now()

        # Post 1 = Current Event
        self.post_1 = Post.objects.create(
            user=self.user_1,
            title='Current Test Post',
            description='Current Test Description',
            location='Current Test Location',
            start_time=now - timedelta(hours=1),
            end_time=now + timedelta(hours=2)
        )
        self.post_1.tags.add(self.tag_1)
        for i in range(5):
            user = User.objects.create_user(
                username=f'liker_1_{i}',
                password='password1'
            )
            Reaction.objects.create(
                post=self.post_1,
                user=user,
                sentiment='LIKE',
                is_attending=True
            )

        # Post 2 = Future Event
        self.post_2 = Post.objects.create(
            user=self.user_2,
            title='Future Test Post',
            description='Future Test Description',
            location='Future Test Location',
            start_time=now + timedelta(days=1),
            end_time=now + timedelta(days=1, hours=2)
        )
        self.post_2.tags.add(self.tag_2)
        for i in range(3):
            user = User.objects.create_user(
                username=f'liker_2_{i}',
                password='password1'
            )
            Reaction.objects.create(
                post=self.post_2,
                user=user,
                sentiment='LIKE',
                is_attending=True
            )

        # Post 3 = Past Event
        self.post_3 = Post.objects.create(
            user=self.user_1,
            title='Past Test Post',
            description='Past Test Description',
            location='Past Test Location',
            start_time=now - timedelta(days=2, hours=2),
            end_time=now - timedelta(days=2)
        )
        self.post_3.tags.add(self.tag_1, self.tag_2)

        # Post 4 = New Event
        self.post_4 = Post.objects.create(
            user=self.user_2,
            title='New Test Post',
            description='New Test Description',
            location='New Test Location',
            start_time=now + timedelta(days=3),
            end_time=now - timedelta(days=3, hours=2)
        )
        self.post_4.tags.add(self.tag_1, self.tag_2)
        user = User.objects.create_user(
                username=f'liker_4',
                password='password1'
            )
        Reaction.objects.create(
            post=self.post_4,
            user=user,
            sentiment='LIKE',
            is_attending=True
        )

    def test_search_view_loads(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/search.html')

    def test_search_view_context(self):
        response = self.client.get(self.url)
        self.assertIn('query', response.context)
        self.assertIn('sort', response.context)
        self.assertIn('tag', response.context)
        self.assertIn('page_obj', response.context)
        self.assertIn('paginator', response.context)
        self.assertIn('now', response.context)
        self.assertIn('tags', response.context)

    def test_search_by_title(self):
        response = self.client.get(self.url, {'q': 'rent Test Pos'})
        posts = response.context['page_obj'].object_list
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0], self.post_1)

    def test_search_by_description(self):
        response = self.client.get(self.url, {'q': 'ure Test Desc'})
        posts = response.context['page_obj'].object_list
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0], self.post_2)

    def test_search_no_results(self):
        response = self.client.get(self.url, {'q': 'Nonexistent'})
        posts = response.context['page_obj'].object_list
        self.assertEqual(len(posts), 0)

    def test_search_empty_query(self):
        response = self.client.get(self.url, {'q': ''})
        posts = response.context['page_obj'].object_list
        self.assertEqual(len(posts), 4)

    def test_filter_by_tag(self):
        response = self.client.get(self.url, {'tag': 'test_tag_1'})
        posts = response.context['page_obj'].object_list
        self.assertEqual(len(posts), 3)
        self.assertIn(self.post_1, posts)
        self.assertIn(self.post_3, posts)
        self.assertIn(self.post_4, posts)

    def test_sort_by_popular(self):
        response = self.client.get(self.url, {'sort': 'popular'})
        posts = response.context['page_obj'].object_list
        self.assertEqual(posts[0], self.post_1)
        self.assertEqual(posts[1], self.post_2)
        self.assertEqual(posts[2], self.post_4)
        self.assertEqual(posts[3], self.post_3)

    def test_sort_by_new(self):
        response = self.client.get(self.url, {'sort': 'new'})
        posts = response.context['page_obj'].object_list
        self.assertEqual(posts[0], self.post_4)
        self.assertEqual(posts[1], self.post_3)
        self.assertEqual(posts[2], self.post_2)
        self.assertEqual(posts[3], self.post_1)

    def test_sort_by_now(self):
        response = self.client.get(self.url, {'sort': 'now'})
        posts = response.context['page_obj'].object_list
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0], self.post_1)
