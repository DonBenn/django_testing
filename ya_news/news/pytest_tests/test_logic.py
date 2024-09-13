from http import HTTPStatus

import pytest
from django.urls import reverse  # type: ignore
from pytest_lazyfixture import lazy_fixture  # type: ignore
from pytest_django.asserts import (assertRedirects,  # type: ignore
                                   assertFormError)  # type: ignore

from news.forms import WARNING, BAD_WORDS
from news.models import Comment


def test_anonymous_user_cant_create_comment(client, news, form_data):

    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'

    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_author_can_create_comment(author_client, author, news, form_data):

    url = reverse('news:detail', args=(news.id,))
    author_client.post(url, data=form_data)

    assert Comment.objects.count() == 1
    comment = Comment.objects.get()

    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_author_cant_use_bad_words(author_client, comment, news, form_data):

    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[1]}, еще текст'}
    form_data['text'] = bad_words_data['text']
    response = author_client.post(url, data=form_data)

    assertFormError(response, 'form', 'text', errors=(WARNING))
    assert Comment.objects.count() == 1


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lazy_fixture('author_client'), HTTPStatus.FOUND),
        (lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND)
    ),
)
def test_author_can_edit_and_other_user_cant_edit_comment(
    form_data,
    comment,
    news,
    parametrized_client,
    expected_status,
    id_for_args
):

    url = reverse('news:edit', args=id_for_args)
    response = parametrized_client.post(url, form_data)

    assert response.status_code == expected_status
    if response.status_code == HTTPStatus.FOUND:
        comment.refresh_from_db()
        comment = Comment.objects.get()
        assert comment.text == form_data['text']
    else:
        comment_from_db = Comment.objects.get(id=news.id)
        assert comment.text == comment_from_db.text


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lazy_fixture('author_client'), HTTPStatus.FOUND),
        (lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND)
    ),
)
def test_author_can_delete_and_other_user_cant_delete_comment(
    parametrized_client,
    expected_status,
    id_for_args
):

    url = reverse('news:delete', args=id_for_args)
    response = parametrized_client.post(url)

    assert response.status_code == expected_status
    if response.status_code == HTTPStatus.NOT_FOUND:
        assert Comment.objects.count() == 1
    else:
        assert Comment.objects.count() == 0
