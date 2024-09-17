from http import HTTPStatus  # type: ignore
from pytils.translit import slugify  # type: ignore

from django.contrib.auth import get_user_model  # type: ignore
from django.test import Client, TestCase  # type: ignore
from django.urls import reverse  # type: ignore

from notes.models import Note
from notes.forms import WARNING
from .base_class import BaseClass

User = get_user_model()


class TestLogic(BaseClass, TestCase):
    """Наследуемый класс для проверки логики"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url = reverse('notes:add')
        cls.slug = 'slug'
        cls.form_data = {
            'title': 'Заголовок5',
            'text': 'Текст5',
            'slug': cls.slug,
        }

        success_url = reverse('notes:success')
        cls.url_to_notes = success_url
        cls.edit_url = reverse('notes:edit', args=(cls.notes.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.notes.slug,))
        cls.form_data_edit = {
            'title': 'Заголовок99',
            'text': cls.NEW_COMMENT_TEXT,
        }

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(self.author)
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.reader_client = Client()
        self.reader_client.force_login(self.reader)

    def test_anonymous_user_cant_create_note(self):
        """Тест: Анонимный пользователь не может создать заметку."""
        notes_count_before_post = Note.objects.count()
        self.client.post(self.url, data=self.form_data)
        notes_count_after_post = Note.objects.count()
        self.assertEqual(notes_count_before_post, notes_count_after_post)

    def test_user_can_create_note(self):
        """Тест: Залогиненный пользователь может создать заметку"""
        notes_count_before_post = Note.objects.count()
        self.auth_client.post(self.url, data=self.form_data)
        notes_count_after_post = Note.objects.count()
        self.assertNotEqual(notes_count_before_post, notes_count_after_post)
        new_note = Note.objects.last()
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_user_cant_create_notes_with_the_same_slug(self):
        """Тест: Невозможно создать две заметки с одинаковым slug."""
        self.auth_client.post(self.url, data=self.form_data)
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.slug + (WARNING)
        )

    def test_slug_can_create_automaticly(self):
        """Тест: Если при создании заметки
        не заполнен slug, то он формируется
        автоматически
        """
        self.form_data.pop('slug')
        self.auth_client.post(self.url, data=self.form_data)
        note = Note.objects.last()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(expected_slug, note.slug)

    def test_author_can_delete_note(self):
        """Тест: Пользователь может  удалять свои заметки"""
        url = reverse('notes:delete', args=(self.notes.slug,))
        response = self.author_client.delete(url)
        self.assertRedirects(response, self.url_to_notes)
        all_notes = Note.objects.all()
        self.assertNotIn(self.notes.slug, all_notes)

    def test_user_cant_delete_note_of_another_user(self):
        """Тест: Пользователь не  может  удалять чужие заметки"""
        url = reverse('notes:delete', args=(self.notes.slug,))
        response = self.reader_client.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.notes.id)
        self.assertEqual(self.notes.slug, note_from_db.slug)

    def test_author_can_edit_note(self):
        """Тест: Пользователь может  редактировать свои заметки"""
        url = reverse('notes:edit', args=(self.notes.slug,))
        notes_count_before_post = Note.objects.count()
        response = self.author_client.post(url,
                                           data=self.form_data_edit)
        notes_count_after_post = Note.objects.count()
        self.assertRedirects(response, self.url_to_notes)
        notes_from_db = Note.objects.get(id=self.notes.id)

        self.assertEqual(notes_from_db.text, self.NEW_COMMENT_TEXT)
        self.assertEqual(notes_from_db.title, self.form_data_edit['title'])

        self.assertEqual(notes_count_before_post, notes_count_after_post)

    def test_user_cant_edit_note_of_another_user(self):
        """Тест: Пользователь не  может  редактировать чужие заметки"""
        url = reverse('notes:edit', args=(self.notes.slug,))
        response = self.reader_client.post(url,
                                           data=self.form_data_edit)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        notes_from_db = Note.objects.get(id=self.notes.id)
        self.assertEqual(self.notes.title, notes_from_db.title)
        self.assertEqual(self.notes.text, notes_from_db.text)
        self.assertEqual(self.notes.slug, notes_from_db.slug)
