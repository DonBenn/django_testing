from django.contrib.auth import get_user_model  # type: ignore

from notes.forms import NoteForm
from .base_fixtures import NotesBaseTestCase

User = get_user_model()


class TestContent(NotesBaseTestCase):
    """Наследуемый класс для проверки контекста"""

    def test_note_in_list_for_author(self):
        """Тест, о том что отдельная заметка передаётся на страницу со
        списком заметок в списке object_list в словаре context
        """
        response = self.author_client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertIn(self.notes, object_list)

    def test_note_not_in_list_for_another_user(self):
        """Тест: в список заметок одного пользователя не попадают
        заметки другого пользователя
        """
        response = self.reader_client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertNotIn(self.notes, object_list)

    def test_authorized_client_has_form(self):
        """Тест: на страницы создания и редактирования заметки
        передаются  формы
        """
        urls = (
            (self.edit_url),
            (self.add_url),
        )
        for name in urls:
            with self.subTest(name=name):
                response = self.author_client.get(name)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
