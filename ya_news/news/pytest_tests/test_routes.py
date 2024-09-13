from http import HTTPStatus

import pytest
from pytest_lazyfixture import lazy_fixture  # type: ignore
from django.urls import reverse  # type: ignore
from pytest_django.asserts import assertRedirects  # type: ignore


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
def test_home_and_registration_availability_for_anonymous_user(client, name):

    url = reverse(name)
    response = client.get(url)

    assert response.status_code == HTTPStatus.OK


def test_news_availability_for_anonymous_user(client, news):

    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lazy_fixture('author_client'), HTTPStatus.OK),
        (lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_comment_availability_for_author_client(
    parametrized_client,
    name,
    id_for_args,
    expected_status
):

    url = reverse(name, args=id_for_args)
    response = parametrized_client.get(url)

    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', lazy_fixture('id_for_args')),
        ('news:delete', lazy_fixture('id_for_args')),
    ),
)
def test_redirect(client, name, args):

    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)

    assertRedirects(response, expected_url)
