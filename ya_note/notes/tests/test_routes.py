from http import HTTPStatus

from django.contrib.auth import get_user_model  # type: ignore
from django.test import Client, TestCase  # type: ignore
from django.urls import reverse  # type: ignore

from .base_class import BaseClass

User = get_user_model()


class TestRoutes(BaseClass, TestCase):
    """Наследуемый класс для проверки маршрутов"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

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
        self.anonim = Client()
        self.author_auth = Client()
        self.author_auth.force_login(self.author)
        self.reader_auth = Client()
        self.reader_auth.force_login(self.reader)

    def test_all_pages_availability(self):
        """Тест на проверку доступности всех страниц
        для разных пользователей
        """
        all_urls = (
            (self.home_url, self.anonim, HTTPStatus.OK),
            (self.home_url, self.author_auth, HTTPStatus.OK),
            (self.login_url, self.anonim, HTTPStatus.OK),
            (self.login_url, self.author_auth, HTTPStatus.OK),
            (self.logout_url, self.anonim, HTTPStatus.OK),
            (self.signup_url, self.anonim, HTTPStatus.OK),
            (self.signup_url, self.author_auth, HTTPStatus.OK),
            (self.list_url, self.author_auth, HTTPStatus.OK),
            (self.add_url, self.author_auth, HTTPStatus.OK),
            (self.success_url, self.author_auth, HTTPStatus.OK),
            (self.edit_url, self.author_auth, HTTPStatus.OK),
            (self.edit_url, self.reader_auth, HTTPStatus.NOT_FOUND),
            (self.delete_url, self.author_auth, HTTPStatus.OK),
            (self.delete_url, self.reader_auth, HTTPStatus.NOT_FOUND),
            (self.detail_url, self.author_auth, HTTPStatus.OK),
            (self.detail_url, self.reader_auth, HTTPStatus.NOT_FOUND),
        )
        for url, user, status in all_urls:
            with self.subTest(url=url, status=status):
                response = user.get(url)
                self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Тест: анонимный пользователь
        перенаправляется на страницу логина
        """
        login_url = reverse('users:login')
        urls = (
            ('notes:edit', self.notes.slug),
            ('notes:delete', self.notes.slug),
            ('notes:detail', self.notes.slug),
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
        )
        for name, args in urls:
            with self.subTest(name=name, args=args):
                url = reverse(name, args=[args] if args else None)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
