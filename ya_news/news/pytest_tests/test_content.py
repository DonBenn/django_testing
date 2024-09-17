import pytest
from pytest_lazyfixture import lazy_fixture  # type: ignore
from django.urls import reverse  # type: ignore
from django.conf import settings  # type: ignore

from news.forms import CommentForm


@pytest.mark.django_db
def test_max_number_of_news_on_home_page(
    news_count_on_home_page, client, home_url
):
    """Тест: Количество новостей на главной странице — не более,
    чем максимально установленное значение
    """
    response = client.get(home_url)
    object_list = response.context['object_list']
    news_count = object_list.count()

    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(news_count_on_home_page, client, home_url):
    """Тест: Новости отсортированы от самой свежей к самой
    старой. Свежие новости в начале списка.
    """
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news_10.date for news_10 in object_list]
    sorted_dates = sorted(all_dates, reverse=True)

    assert all_dates == sorted_dates


def test_comments_order(ten_comments_fixture, news, client):
    """Тест: Комментарии на странице отдельной новости
    отсортированы в хронологическом порядке
    """
    detail_url = reverse('news:detail', args=(news.id,))
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.parametrize(
    'parametrized_client, expected_form',
    (
        (lazy_fixture('author_client'), True),
        (lazy_fixture('not_author_client'), False)
    ),
)
def test_author_can_get_and_other_user_cant_get_form_for_comment(
    news,
    parametrized_client,
    expected_form,
    comment
):
    """Тест: Анонимному пользователю недоступна форма для отправки комментария
    на странице отдельной новости, а авторизованному доступна.
    """
    url = reverse('news:edit', args=(comment.id,))
    response = parametrized_client.get(url)

    if expected_form:
        assert 'form' in response.context
        assert isinstance(response.context['form'], CommentForm)
    else:
        assert 'form' not in response.context
