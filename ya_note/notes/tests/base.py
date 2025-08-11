from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='Автор')
        cls.not_author = User.objects.create_user(username='Не автор')

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author
        )

        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)

        cls.anonymous_client = Client()

        cls.NOTES_LIST_URL = reverse('notes:list')
        cls.NOTES_ADD_URL = reverse('notes:add')
        cls.NOTES_EDIT_URL = reverse('notes:edit', args=(cls.note.slug,))
        cls.NOTES_DELETE_URL = reverse('notes:delete', args=(cls.note.slug,))
        cls.NOTES_SUCCESS_URL = reverse('notes:success')
        cls.NOTES_DETAIL_URL = reverse('notes:detail', args=(cls.note.slug,))
        cls.NOTES_HOME_URL = reverse('notes:home')
        cls.USERS_LOGIN_URL = reverse('users:login')
        cls.USERS_SIGNUP_URL = reverse('users:signup')
