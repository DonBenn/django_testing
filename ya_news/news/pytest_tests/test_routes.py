from http import HTTPStatus

import pytest
from pytest_lazyfixture import lazy_fixture  # type: ignore
from pytest_django.asserts import assertRedirects  # type: ignore

from .test_logic import FORM_DATA


@pytest.mark.django_db
@pytest.mark.parametrize(

    'page, parametrized_client, expected_status',
    (
        (lazy_fixture('home_url'), lazy_fixture('client'), HTTPStatus.OK),
        (lazy_fixture('home_url'), lazy_fixture('author_client'),
         HTTPStatus.OK),
        (lazy_fixture('home_url'), lazy_fixture('not_author_client'),
         HTTPStatus.OK),
        (lazy_fixture('login_url'), lazy_fixture('client'), HTTPStatus.OK),
        (lazy_fixture('login_url'), lazy_fixture('author_client'),
         HTTPStatus.OK),
        (lazy_fixture('login_url'), lazy_fixture('not_author_client'),
         HTTPStatus.OK),
        (lazy_fixture('signup_url'), lazy_fixture('client'), HTTPStatus.OK),
        (lazy_fixture('signup_url'), lazy_fixture('author_client'),
         HTTPStatus.OK),
        (lazy_fixture('signup_url'), lazy_fixture('not_author_client'),
         HTTPStatus.OK),
        (lazy_fixture('detail_url'), lazy_fixture('client'), HTTPStatus.OK),
        (lazy_fixture('detail_url'), lazy_fixture('author_client'),
         HTTPStatus.OK),
        (lazy_fixture('detail_url'), lazy_fixture('not_author_client'),
         HTTPStatus.OK),
        (lazy_fixture('edit_url'), lazy_fixture('client'),
         HTTPStatus.FOUND),
        (lazy_fixture('edit_url'), lazy_fixture('author_client'),
         HTTPStatus.OK),
        (lazy_fixture('edit_url'), lazy_fixture('not_author_client'),
         HTTPStatus.NOT_FOUND),
        (lazy_fixture('delete_url'), lazy_fixture('client'),
         HTTPStatus.FOUND),
        (lazy_fixture('delete_url'), lazy_fixture('author_client'),
         HTTPStatus.OK),
        (lazy_fixture('delete_url'), lazy_fixture('not_author_client'),
         HTTPStatus.NOT_FOUND),
        (lazy_fixture('logout_url'), lazy_fixture('client'),
         HTTPStatus.OK),
        (lazy_fixture('logout_url'), lazy_fixture('author_client'),
         HTTPStatus.OK),
        (lazy_fixture('logout_url'), lazy_fixture('not_author_client'),
         HTTPStatus.OK),
    ),
)
def test_home_and_registration_availability_for_anonymous_user(
    parametrized_client, expected_status, page
):
    """Тест на доступность страниц разным пользователям"""
    response = parametrized_client.get(page)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    (
        (lazy_fixture('edit_url')),
        (lazy_fixture('delete_url')),
        (lazy_fixture('detail_url')),
    ),
)
def test_redirect(client, name, detail_url, edit_url, delete_url, login_url):
    """Тест: При попытке перейти на страницу отправки, редактирования, удаления
    комментария анонимный пользователь перенаправляется на страницу
    авторизации
    """
    expected_url = f'{login_url}?next={name}'
    if name == edit_url or name == delete_url:
        response = client.get(name)
    elif name == detail_url:
        response = client.post(name, data=FORM_DATA)
    assertRedirects(response, expected_url)
