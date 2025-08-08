import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from news.models import Comment, News

User = get_user_model()


@pytest.fixture
def author():
    """Фикстура для создания автора."""
    return User.objects.create_user(username='Автор')


@pytest.fixture
def reader():
    return User.objects.create_user(username='Читатель')


@pytest.fixture
def news():
    return News.objects.create(
        title='Заголовок',
        text='Текст',
        date=timezone.now()
    )


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def multiple_news():
    now = timezone.now()
    news_list = []
    for i in range(15):
        news = News.objects.create(
            title=f'Новость {i}',
            text=f'Текст новости {i}',
            date=now - timedelta(hours=i)
        )
        news_list.append(news)
    return news_list


@pytest.fixture
def multiple_comments(news, author, reader):
    now = timezone.now()
    comments = []
    old_comment = Comment.objects.create(
        news=news,
        author=author,
        text='Старый комментарий',
        created=now - timedelta(hours=2)
    )
    comments.append(old_comment)
    middle_comment = Comment.objects.create(
        news=news,
        author=reader,
        text='Средний комментарий',
        created=now - timedelta(hours=1)
    )
    comments.append(middle_comment)
    new_comment = Comment.objects.create(
        news=news,
        author=author,
        text='Новый комментарий',
        created=now
    )
    comments.append(new_comment)
    return comments
