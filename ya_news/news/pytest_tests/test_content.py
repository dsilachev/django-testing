import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings

from news.forms import CommentForm

User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def news_detail_url(news):
    return reverse('news:detail', args=(news.id,))


def test_news_count_on_home_page(client, multiple_news, home_url):
    response = client.get(home_url)
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order_on_home_page(client, multiple_news, home_url):
    response = client.get(home_url)
    object_list = list(response.context['object_list'])
    sorted_list = sorted(object_list, key=lambda n: n.date, reverse=True)
    assert object_list == sorted_list


def test_comments_order_on_news_detail_page(
    client, news, multiple_comments, news_detail_url
):
    response = client.get(news_detail_url)
    comments = list(response.context['news'].comment_set.all())
    sorted_comments = sorted(comments, key=lambda c: c.created)
    assert comments == sorted_comments


def test_anonymous_user_has_no_form(client, news_detail_url):
    response = client.get(news_detail_url)
    assert 'form' not in response.context


def test_authorized_user_has_form(client, news_detail_url, author):
    client.force_login(author)
    response = client.get(news_detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
