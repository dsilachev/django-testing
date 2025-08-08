import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from news.forms import CommentForm
from news.models import Comment, News

User = get_user_model()


@pytest.mark.django_db
def test_news_count_on_home_page(client):
    for i in range(15):
        News.objects.create(
            title=f'Новость {i}',
            text=f'Текст новости {i}'
        )
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert len(object_list) == 10


@pytest.mark.django_db
def test_news_order_on_home_page(client):
    now = timezone.now()
    old_news = News.objects.create(
        title='Старая новость',
        text='Текст старой новости',
        date=now - timedelta(days=2)
    )
    middle_news = News.objects.create(
        title='Средняя новость',
        text='Текст средней новости',
        date=now - timedelta(days=1)
    )
    fresh_news = News.objects.create(
        title='Свежая новость',
        text='Текст свежей новости',
        date=now
    )
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert object_list[0] == fresh_news
    assert object_list[1] == middle_news
    assert object_list[2] == old_news


@pytest.mark.django_db
def test_comments_order_on_news_detail_page(client, news, author, reader):
    now = timezone.now()
    old_comment = Comment.objects.create(
        news=news,
        author=author,
        text='Старый комментарий',
        created=now - timedelta(hours=2)
    )
    middle_comment = Comment.objects.create(
        news=news,
        author=reader,
        text='Средний комментарий',
        created=now - timedelta(hours=1)
    )
    new_comment = Comment.objects.create(
        news=news,
        author=author,
        text='Новый комментарий',
        created=now
    )
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    all_comments = list(response.context['news'].comment_set.all())
    assert all_comments[0] == old_comment
    assert all_comments[1] == middle_comment
    assert all_comments[2] == new_comment


@pytest.mark.django_db
def test_anonymous_user_has_no_form(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_user_has_form(client, news, author):
    client.force_login(author)
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
