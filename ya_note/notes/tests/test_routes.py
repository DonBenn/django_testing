from http import HTTPStatus

from django.contrib.auth import get_user_model  # type: ignore

from .base_fixtures import NotesBaseTestCase

User = get_user_model()


class TestRoutes(NotesBaseTestCase):
    """Наследуемый класс для проверки маршрутов"""

    def test_all_pages_availability(self):
        """Тест на проверку доступности всех страниц
        для разных пользователей
        """
        all_urls = (
            (self.home_url, self.client, HTTPStatus.OK),
            (self.home_url, self.author_client, HTTPStatus.OK),
            (self.home_url, self.reader_client, HTTPStatus.OK),
            (self.login_url, self.client, HTTPStatus.OK),
            (self.login_url, self.author_client, HTTPStatus.OK),
            (self.login_url, self.reader_client, HTTPStatus.OK),
            (self.signup_url, self.client, HTTPStatus.OK),
            (self.signup_url, self.author_client, HTTPStatus.OK),
            (self.signup_url, self.reader_client, HTTPStatus.OK),
            (self.list_url, self.client, HTTPStatus.FOUND),
            (self.list_url, self.author_client, HTTPStatus.OK),
            (self.list_url, self.reader_client, HTTPStatus.OK),
            (self.add_url, self.client, HTTPStatus.FOUND),
            (self.add_url, self.author_client, HTTPStatus.OK),
            (self.add_url, self.reader_client, HTTPStatus.OK),
            (self.success_url, self.client, HTTPStatus.FOUND),
            (self.success_url, self.author_client, HTTPStatus.OK),
            (self.success_url, self.author_client, HTTPStatus.OK),
            (self.edit_url, self.client, HTTPStatus.FOUND),
            (self.edit_url, self.author_client, HTTPStatus.OK),
            (self.edit_url, self.reader_client, HTTPStatus.NOT_FOUND),
            (self.delete_url, self.client, HTTPStatus.FOUND),
            (self.delete_url, self.author_client, HTTPStatus.OK),
            (self.delete_url, self.reader_client, HTTPStatus.NOT_FOUND),
            (self.detail_url, self.client, HTTPStatus.FOUND),
            (self.detail_url, self.author_client, HTTPStatus.OK),
            (self.detail_url, self.reader_client, HTTPStatus.NOT_FOUND),
            (self.logout_url, self.client, HTTPStatus.OK),
            (self.logout_url, self.author_client, HTTPStatus.OK),
            (self.logout_url, self.reader_client, HTTPStatus.OK),
        )
        for url, user, status in all_urls:
            with self.subTest(url=url, status=status):
                response = user.get(url)
                self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Тест: анонимный пользователь
        перенаправляется на страницу логина
        """
        urls = (
            (self.edit_url),
            (self.delete_url),
            (self.detail_url),
            (self.list_url),
            (self.add_url),
            (self.success_url),
        )
        for name in urls:
            with self.subTest(name=name):
                redirect_url = f'{self.login_url}?next={name}'
                response = self.client.get(name)
                self.assertRedirects(response, redirect_url)
