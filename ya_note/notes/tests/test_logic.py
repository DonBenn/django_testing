from http import HTTPStatus  # type: ignore
from pytils.translit import slugify  # type: ignore

from django.contrib.auth import get_user_model  # type: ignore

from notes.models import Note
from notes.forms import WARNING
from .fixtures import Fixtures

User = get_user_model()


class TestLogic(Fixtures):
    """Наследуемый класс для проверки логики"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.slug = 'slug'
        cls.form_data = {
            'title': 'Заголовок5',
            'text': 'Текст5',
            'slug': cls.slug,
        }
        cls.form_data_edit = {
            'title': 'Заголовок99',
            'text': cls.NEW_COMMENT_TEXT,
        }

    def test_anonymous_user_cant_create_note(self):
        """Тест: Анонимный пользователь не может создать заметку."""
        notes_count_before_post = Note.objects.count()
        self.client.post(self.add_url, data=self.form_data)
        notes_count_after_post = Note.objects.count()
        self.assertEqual(notes_count_before_post, notes_count_after_post)

    def test_user_can_create_note(self):
        """Тест: Залогиненный пользователь может создать заметку"""
        notes_set_before_post = set(Note.objects.all())
        self.author_client.post(self.add_url, data=self.form_data)
        notes_set_after_post = set(Note.objects.all())
        sam_note = notes_set_after_post.difference(notes_set_before_post)
        new_note = sam_note.pop()

        self.assertEqual(len(notes_set_before_post),
                         len(notes_set_after_post) - 1)
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_user_cant_create_notes_with_the_same_slug(self):
        """Тест: Невозможно создать две заметки с одинаковым slug."""
        self.author_client.post(self.add_url, data=self.form_data)
        notes_count_before_post = Note.objects.count()
        response = self.author_client.post(self.add_url, data=self.form_data)
        notes_count_after_post = Note.objects.count()

        self.assertEqual(notes_count_before_post, notes_count_after_post)
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
        notes_set_before_post = set(Note.objects.all())
        self.author_client.post(self.add_url, data=self.form_data)
        notes_set_after_post = set(Note.objects.all())
        set_difference = notes_set_after_post.difference(notes_set_before_post)
        note_from_db = set_difference.pop()
        expected_slug = slugify(self.form_data['title'])

        self.assertEqual(expected_slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        """Тест: Пользователь может  удалять свои заметки"""
        notes_count_before_post = Note.objects.count()
        response = self.author_client.delete(self.delete_url)
        notes_count_after_post = Note.objects.count()

        self.assertEqual(notes_count_before_post - 1, notes_count_after_post)
        self.assertRedirects(response, self.success_url)

    def test_user_cant_delete_note_of_another_user(self):
        """Тест: Пользователь не  может  удалять чужие заметки"""
        notes_count_before_post = Note.objects.count()
        response = self.reader_client.delete(self.delete_url)
        notes_count_after_post = Note.objects.count()
        note_from_db = Note.objects.get(id=self.notes.id)

        self.assertEqual(notes_count_before_post, notes_count_after_post)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(self.notes.slug, note_from_db.slug)
        self.assertEqual(self.notes.title, note_from_db.title)
        self.assertEqual(self.notes.text, note_from_db.text)
        self.assertEqual(self.notes.author, note_from_db.author)

    def test_author_can_edit_note(self):
        """Тест: Пользователь может  редактировать свои заметки"""
        notes_count_before_post = Note.objects.count()
        response = self.author_client.post(self.edit_url,
                                           data=self.form_data_edit)
        notes_count_after_post = Note.objects.count()
        notes_from_db = Note.objects.get(id=self.notes.id)

        self.assertRedirects(response, self.success_url)
        self.assertEqual(notes_from_db.text, self.NEW_COMMENT_TEXT)
        self.assertEqual(notes_from_db.title, self.form_data_edit['title'])
        self.assertEqual(notes_from_db.author, self.author)
        self.assertEqual(notes_from_db.slug,
                         slugify(self.form_data_edit['title']))
        self.assertEqual(notes_count_before_post, notes_count_after_post)

    def test_user_cant_edit_note_of_another_user(self):
        """Тест: Пользователь не  может  редактировать чужие заметки"""
        notes_count_before_post = Note.objects.count()
        response = self.reader_client.post(self.edit_url,
                                           data=self.form_data_edit)
        notes_count_after_post = Note.objects.count()
        notes_from_db = Note.objects.get(id=self.notes.id)

        self.assertEqual(notes_count_before_post, notes_count_after_post)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(self.notes.title, notes_from_db.title)
        self.assertEqual(self.notes.text, notes_from_db.text)
        self.assertEqual(self.notes.slug, notes_from_db.slug)
        self.assertEqual(self.notes.author, notes_from_db.author)
