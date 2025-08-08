from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from django.contrib.auth import get_user_model


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = get_user_model().objects.create_user(username='Автор')
        cls.not_author = get_user_model().objects.create_user(username='Не автор')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )
        cls.slug = cls.note.slug
        cls.slug_args = (cls.slug,)

    def setUp(self):
        self.client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.not_author_client = Client()
        self.not_author_client.force_login(self.not_author)

    def test_home_availability_for_anonymous_user(self):
        url = reverse('notes:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_anonymous_user(self):
        url_names = ('notes:home', 'users:login', 'users:signup')
        for name in url_names:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_logout_get_method_not_allowed(self):
        url = reverse('users:logout')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_logout_post_redirect(self):
        url = reverse('users:logout')
        response = self.client.post(url)
        self.assertIn(response.status_code, (HTTPStatus.OK, HTTPStatus.FOUND, HTTPStatus.SEE_OTHER))

    def test_pages_availability_for_authenticated_user(self):
        url_names = ('notes:list', 'notes:add', 'notes:success')
        for name in url_names:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.not_author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_exists(self):
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
        self.assertEqual(self.note.title, 'Заголовок')

    def test_empty_database(self):
        Note.objects.all().delete()
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_pages_availability_for_author(self):
        url_names = ('notes:detail', 'notes:edit', 'notes:delete')
        for name in url_names:
            with self.subTest(name=name):
                url = reverse(name, args=self.slug_args)
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        url_names = ('notes:detail', 'notes:edit', 'notes:delete')
        test_cases = (
            (self.author_client, HTTPStatus.OK),
            (self.not_author_client, HTTPStatus.NOT_FOUND),
        )
        for name in url_names:
            for client, expected_status in test_cases:
                with self.subTest(name=name, client=client):
                    url = reverse(name, args=self.slug_args)
                    response = client.get(url)
                    self.assertEqual(response.status_code, expected_status)

    def test_redirects_for_anonymous_user(self):
        protected_urls = (
            ('notes:detail', self.slug_args),
            ('notes:edit', self.slug_args),
            ('notes:delete', self.slug_args),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None),
        )
        login_url = reverse('users:login')
        for name, args in protected_urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                expected_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, expected_url)
