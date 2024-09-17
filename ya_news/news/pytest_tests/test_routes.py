from http import HTTPStatus

import pytest
from pytest_lazyfixture import lazy_fixture  # type: ignore
from django.urls import reverse  # type: ignore
from pytest_django.asserts import assertRedirects  # type: ignore


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lazy_fixture('author_client'), HTTPStatus.OK),
        (lazy_fixture('not_author_client'), HTTPStatus.OK),
        (lazy_fixture('client'), HTTPStatus.OK),
    ),
)
@pytest.mark.parametrize(
    'name, args',
    (('news:home', None),
     ('users:login', None),
     ('users:logout', None),
     ('users:signup', None),
     ('news:detail', True),
     ('news:edit', True),
     ('news:delete', True)
     )
)
def test_home_and_registration_availability_for_anonymous_user(
    client, name, news, args, comment, parametrized_client, expected_status,
    not_author_client, author_client
):
    """Тест на доступность страниц разным пользователям"""
    if args:
        if 'detail' in name:
            url = reverse(name, args=(news.id,))
            response = parametrized_client.get(url)
            assert response.status_code == expected_status
        elif 'edit' or 'delete' in name:
            url = reverse(name, args=(comment.id,))
            response = client.get(url)
            assert response.status_code == HTTPStatus.FOUND
            response = not_author_client.get(url)
            assert response.status_code == HTTPStatus.NOT_FOUND
            response = author_client.get(url)
            assert response.status_code == HTTPStatus.OK
    else:
        url = reverse(name)
        response = parametrized_client.get(url)
        assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', lazy_fixture('comment')),
        ('news:delete', lazy_fixture('comment')),
    ),
)
def test_redirect(client, name, args):
    """Тест: При попытке перейти на страницу редактирования или удаления
    комментария анонимный пользователь перенаправляется на страницу
    авторизации
    """
    login_url = reverse('users:login')
    url = reverse(name, args=(args.id,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)

    assertRedirects(response, expected_url)
