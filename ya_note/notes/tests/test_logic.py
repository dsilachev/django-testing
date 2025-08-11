from django.utils.text import slugify
from django.urls import reverse
from http import HTTPStatus

from notes.forms import WARNING
from notes.models import Note
from .base import BaseTestCase


class TestLogic(BaseTestCase):

    def setUp(self):
        self.form_data = {
            'title': 'zagolovok',
            'text': 'text',
            'slug': 'new-slug',
        }

    def test_user_can_create_note(self):
        notes_before = Note.objects.count()
        response = self.author_client.post(
            self.NOTES_ADD_URL, data=self.form_data
        )
        self.assertRedirects(response, self.NOTES_SUCCESS_URL)
        notes_after = Note.objects.count()
        self.assertEqual(notes_after, notes_before + 1)

        new_note = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        notes_before = Note.objects.count()
        response = self.anonymous_client.post(
            self.NOTES_ADD_URL, data=self.form_data
        )
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.NOTES_ADD_URL}'
        self.assertRedirects(response, expected_url)
        notes_after = Note.objects.count()
        self.assertEqual(notes_after, notes_before)

    def test_not_unique_slug(self):
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(
            self.NOTES_ADD_URL, data=self.form_data
        )
        form = response.context.get('form')
        self.assertIsNotNone(form)
        self.assertTrue(form.errors)
        self.assertIn('slug', form.errors)
        self.assertIn(self.note.slug + WARNING, form.errors['slug'])
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        Note.objects.all().delete()
        form_data = {
            'title': 'zagolovok',
            'text': 'text',
        }
        response = self.author_client.post(self.NOTES_ADD_URL, data=form_data)
        self.assertRedirects(response, self.NOTES_SUCCESS_URL)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.NOTES_EDIT_URL, self.form_data)
        self.assertRedirects(response, self.NOTES_SUCCESS_URL)

        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.title, self.form_data['title'])
        self.assertEqual(updated_note.text, self.form_data['text'])
        self.assertEqual(updated_note.slug, self.form_data['slug'])
        self.assertEqual(updated_note.author, self.author)

    def test_other_user_cant_edit_note(self):
        response = self.not_author_client.post(
            self.NOTES_EDIT_URL, self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(note_from_db.title, self.note.title)
        self.assertEqual(note_from_db.text, self.note.text)
        self.assertEqual(note_from_db.slug, self.note.slug)
        self.assertEqual(note_from_db.author, self.note.author)

    def test_author_can_delete_note(self):
        response = self.author_client.post(self.NOTES_DELETE_URL)
        self.assertRedirects(response, self.NOTES_SUCCESS_URL)
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        response = self.not_author_client.post(self.NOTES_DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(note_from_db.title, self.note.title)
        self.assertEqual(note_from_db.text, self.note.text)
        self.assertEqual(note_from_db.slug, self.note.slug)
        self.assertEqual(note_from_db.author, self.note.author)
