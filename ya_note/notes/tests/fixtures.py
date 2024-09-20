from django.test import TestCase, Client  # type: ignore  #Client,
from django.urls import reverse  # type: ignore
from django.contrib.auth import get_user_model  # type: ignore

from notes.models import Note

User = get_user_model()


class Fixtures(TestCase):
    """Базовый класс для фикстур"""

    HOME_URL = reverse('notes:home')
    LIST_URL = reverse('notes:list')
    COMMENT_TEXT = 'Текст комментария'
    NEW_COMMENT_TEXT = 'Обновлённый комментарий'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.notes = Note.objects.create(
            title='Заголовок3',
            author=cls.author,
            text=cls.COMMENT_TEXT,
        )
        cls.home_url = reverse('notes:home')
        cls.login_url = reverse('users:login')
        cls.logout_url = reverse('users:logout')
        cls.signup_url = reverse('users:signup')
        cls.list_url = reverse('notes:list')
        cls.add_url = reverse('notes:add')
        cls.success_url = reverse('notes:success')
        cls.edit_url = reverse('notes:edit', args=(cls.notes.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.notes.slug,))
        cls.detail_url = reverse('notes:detail', args=(cls.notes.slug,))

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.reader_client = Client()
        self.reader_client.force_login(self.reader)
