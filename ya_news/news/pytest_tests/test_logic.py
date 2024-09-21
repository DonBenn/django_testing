from http import HTTPStatus

from pytest_django.asserts import assertFormError  # type: ignore

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
    comments_at_the_start_test = set(Comment.objects.all())
    author_client.post(detail_url, data=FORM_DATA)
    comments_at_the_end_test = set(Comment.objects.all())
    set_difference = comments_at_the_end_test.difference(
        comments_at_the_start_test
    )
    comment_from_db = set_difference.pop()

    assert len(comments_at_the_end_test) == len(comments_at_the_start_test) + 1
    assert comment_from_db.text == FORM_DATA['text']
    assert comment_from_db.news == news
    assert comment_from_db.author == author


def test_author_can_edit_comment(
        author_client, comment, news, author, edit_url):
    """Тест: Авторизованный пользователь может редактировать
    свои комментарии.
    """
    comments_at_the_start_test = Comment.objects.count()
    author_client.post(edit_url, data=FORM_DATA)
    comments_at_the_end_test = Comment.objects.count()
    comment_from_db = Comment.objects.get(id=comment.id)

    assert comments_at_the_start_test == comments_at_the_end_test
    assert comment_from_db.text == FORM_DATA['text']
    assert comment_from_db.news == news
    assert comment_from_db.author == author
    assert comment_from_db.created == comment.created


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
    comment_id = comment.id
    author_client.post(delete_url)
    comments_at_the_end_test = Comment.objects.count()

    assert comments_at_the_end_test == comments_at_the_start_test - 1
    assert Comment.objects.filter(id=comment_id).exists() is False


def test_other_user_cant_delete_comment(
        not_author_client, comment, news, author, delete_url
):
    """Авторизованный пользователь не может удалять
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
