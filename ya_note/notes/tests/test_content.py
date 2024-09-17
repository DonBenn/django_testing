from django.test import TestCase, Client  # type: ignore
from django.urls import reverse  # type: ignore
from django.contrib.auth import get_user_model  # type: ignore

from notes.forms import NoteForm
from .base_class import BaseClass

User = get_user_model()


class TestContent(BaseClass, TestCase):
    """Наследуемый класс для проверки контекста"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

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
        self.client.force_login(self.reader)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertNotIn(self.notes, object_list)

    def test_authorized_client_has_form(self):
        """Тест: на страницы создания и редактирования заметки
        передаются  формы
        """
        urls = (
            ('notes:edit', self.notes.slug),
            ('notes:add', None),
        )
        for name, args in urls:
            with self.subTest(name=name, args=args):
                url = reverse(name, args=[args] if args else None)
                response = self.author_client.get(url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
