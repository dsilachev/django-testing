from notes.forms import NoteForm
from .base import BaseTestCase


class TestContent(BaseTestCase):

    def test_note_in_list_for_author(self):
        response = self.author_client.get(self.NOTES_LIST_URL)
        object_list = response.context['object_list']
        self.assertEqual(list(object_list), [self.note])

    def test_note_not_in_list_for_another_user(self):
        response = self.not_author_client.get(self.NOTES_LIST_URL)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_create_and_edit_note_page_contains_form(self):
        urls = (
            (self.NOTES_ADD_URL, 'Добавление'),
            (self.NOTES_EDIT_URL, 'Редактирование'),
        )
        for url, name in urls:
            with self.subTest(page=name):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
