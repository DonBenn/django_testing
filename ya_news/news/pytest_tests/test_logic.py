from http import HTTPStatus

from django.urls import reverse  # type: ignore
from pytest_django.asserts import (assertRedirects,  # type: ignore
                                   assertFormError)  # type: ignore

from news.forms import WARNING, BAD_WORDS
from news.models import Comment

FORM_DATA = {'text': 'Новый текст New'}


def test_anonymous_user_cant_create_comment(client, news, ):
    """Тест: Анонимный пользователь не может отправить
    комментарий.
    """
    comments_at_the_start_test = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, data=FORM_DATA)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'

    assertRedirects(response, expected_url)
    comments_at_the_end_test = Comment.objects.count()
    assert comments_at_the_start_test == comments_at_the_end_test


def test_author_can_create_comment(author_client, author, news):
    """Авторизованный пользователь может отправить комментарий."""
    url = reverse('news:detail', args=(news.id,))
    author_client.post(url, data=FORM_DATA)

    assert Comment.objects.count() == 1
    comment = Comment.objects.get()

    assert comment.text == FORM_DATA['text']
    assert comment.news == news
    assert comment.author == author


def test_author_can_edit_comment(author_client, comment, news):
    """Тест: Авторизованный пользователь может редактировать
    свои комментарии.
    """
    comments_at_the_start_test = Comment.objects.count()
    url = reverse('news:edit', args=(comment.id,))
    author_client.post(url, FORM_DATA)
    comment = Comment.objects.get()
    assert comment.text == FORM_DATA['text']
    comments_at_the_end_test = Comment.objects.count()
    assert comments_at_the_start_test == comments_at_the_end_test


def test_other_user_cant_edit_comment(not_author_client, comment, news):
    """Тест: Авторизованный пользователь не может редактировать
    чужие комментарии.
    """
    url = reverse('news:edit', args=(comment.id,))
    response = not_author_client.post(url, FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=news.id)
    assert comment.text == comment_from_db.text


def test_author_can_delete_comment(author_client, comment):
    """Тест: Авторизованный пользователь может  удалять
    свои комментарии.
    """
    url = reverse('news:delete', args=(comment.id,))
    author_client.post(url)
    all_comments = Comment.objects.all()

    assert comment.id not in all_comments


def test_other_user_cant_delete_comment(not_author_client, comment):
    """Авторизованный пользователь не может или удалять
    чужие комментарии.
    """
    url = reverse('news:delete', args=(comment.id,))
    response = not_author_client.post(url)
    comment_from_db = Comment.objects.get(id=comment.id)

    assert comment.text == comment_from_db.text
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_author_cant_use_bad_words(author_client, comment, news):
    """Тест: Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[1]}, еще текст'}
    FORM_DATA['text'] = bad_words_data['text']
    response = author_client.post(url, data=FORM_DATA)

    assertFormError(response, 'form', 'text', errors=(WARNING))
    assert Comment.objects.count() == 1
