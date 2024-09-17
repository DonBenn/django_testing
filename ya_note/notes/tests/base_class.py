from django.test import TestCase  # type: ignore  #Client,
from django.urls import reverse  # type: ignore
from django.contrib.auth import get_user_model  # type: ignore

from notes.models import Note

User = get_user_model()


class BaseClass(TestCase):
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
