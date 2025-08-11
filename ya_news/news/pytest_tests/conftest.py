import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta

from news.models import Comment, News
from news.forms import BAD_WORDS

User = get_user_model()


@pytest.fixture
def author():
    """Фикстура для создания автора."""
    return User.objects.create_user(username='Автор')


@pytest.fixture
def reader():
    return User.objects.create_user(username='Читатель')


@pytest.fixture
def author_client(client, author):
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(client, reader):
    client.force_login(reader)
    return client


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
    news_list = [
        News(
            title=f'Новость {i}',
            text=f'Текст новости {i}',
            date=now - timedelta(hours=i)
        )
        for i in range(15)
    ]
    News.objects.bulk_create(news_list)


@pytest.fixture
def multiple_comments(news, author, reader):
    users = [author, reader, author]
    texts = ['Старый комментарий', 'Средний комментарий', 'Новый комментарий']
    comments = [
        Comment(news=news, author=users[i], text=texts[i])
        for i in range(3)
    ]
    Comment.objects.bulk_create(comments)


@pytest.fixture
def form_data():
    return {'text': 'Текст комментария'}


@pytest.fixture
def bad_words_data():
    return {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def news_detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def comment_urls(comment):
    news_url = reverse('news:detail', args=(comment.news.id,))
    return {
        'news_url': news_url,
        'delete_url': reverse('news:delete', args=(comment.id,)),
        'edit_url': reverse('news:edit', args=(comment.id,))
    }
