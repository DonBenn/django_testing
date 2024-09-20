from http import HTTPStatus

from django.utils import timezone  # type: ignore
from pytest_django.asserts import (assertFormError)  # type: ignore

from news.forms import WARNING, BAD_WORDS
from news.models import Comment

FORM_DATA = {'text': 'Новый текст New'}


def test_anonymous_user_cant_create_comment(client, detail_url):
    """Тест: Анонимный пользователь не может отправить
    комментарий.
    """
    comments_at_the_start_test = Comment.objects.count()
    client.post(detail_url, data=FORM_DATA)
    comments_at_the_end_test = Comment.objects.count()

    assert comments_at_the_start_test == comments_at_the_end_test


def test_author_can_create_comment(author_client, author, news, detail_url):
    """Авторизованный пользователь может отправить комментарий."""
    comments_at_the_start_test = list(
        Comment.objects.filter(news=news).exclude(created__lte=timezone.now())
    )
    author_client.post(detail_url, data=FORM_DATA)
    comments_at_the_end_test = list(Comment.objects.filter(news=news))

    assert len(comments_at_the_end_test) == len(comments_at_the_start_test) + 1
    assert comments_at_the_end_test[0].text == FORM_DATA['text']
    assert comments_at_the_end_test[0].news == news
    assert comments_at_the_end_test[0].author == author


def test_author_can_edit_comment(
        author_client, comment, news, author, edit_url):
    """Тест: Авторизованный пользователь может редактировать
    свои комментарии.
    """
    comments_at_the_start_test = Comment.objects.count()
    author_client.post(edit_url, data=FORM_DATA)
    comments_at_the_end_test = Comment.objects.count()
    comment_request = Comment.objects.filter(news=news)
    comment_from_db = list(comment_request)

    assert comments_at_the_start_test == comments_at_the_end_test
    assert comment_from_db[0].text == FORM_DATA['text']
    assert comment_from_db[0].news == news
    assert comment_from_db[0].author == author
    assert comment_from_db[0].created == comment.created


def test_other_user_cant_edit_comment(
        not_author_client, author, comment, news, edit_url
):
    """Тест: Авторизованный пользователь не может редактировать
    чужие комментарии.
    """
    comments_at_the_start_test = Comment.objects.count()
    response = not_author_client.post(edit_url, FORM_DATA)
    comments_at_the_end_test = Comment.objects.count()
    comment_from_db = Comment.objects.get(id=comment.id)

    assert comments_at_the_start_test == comments_at_the_end_test
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comment.text == comment_from_db.text
    assert comment.news == news
    assert comment.author == author
    assert comment.created == comment_from_db.created


def test_author_can_delete_comment(author_client, comment, delete_url):
    """Тест: Авторизованный пользователь может  удалять
    свои комментарии.
    """
    comments_at_the_start_test = Comment.objects.count()
    author_client.post(delete_url)
    comments_at_the_end_test = Comment.objects.count()
    assert comments_at_the_end_test == comments_at_the_start_test - 1


def test_other_user_cant_delete_comment(
        not_author_client, comment, news, author, delete_url
):
    """Авторизованный пользователь не может или удалять
    чужие комментарии.
    """
    comments_at_the_start_test = Comment.objects.count()
    response = not_author_client.post(delete_url)
    comments_at_the_end_test = Comment.objects.count()
    comment_from_db = Comment.objects.get(id=comment.id)

    assert comments_at_the_start_test == comments_at_the_end_test
    assert comment.text == comment_from_db.text
    assert comment.news == news
    assert comment.author == author
    assert comment.created == comment_from_db.created
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_author_cant_use_bad_words(
        author_client, comment, news, author, detail_url
):
    """Тест: Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[1]}, еще текст'}
    FORM_DATA['text'] = bad_words_data['text']
    comments_at_the_start_test = Comment.objects.count()
    response = author_client.post(detail_url, data=FORM_DATA)
    comments_at_the_end_test = Comment.objects.count()
    comment_from_db = Comment.objects.get(id=comment.id)

    assertFormError(response, 'form', 'text', errors=(WARNING))

    assert comments_at_the_start_test == comments_at_the_end_test
    assert comment.text == comment_from_db.text
    assert comment.news == news
    assert comment.author == author
    assert comment.created == comment_from_db.created
