from http import HTTPStatus

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'name, args, client_fixture, expected_status',
    [
        ('news:home', None, 'client', HTTPStatus.OK),
        ('news:detail', 'news_id', 'client', HTTPStatus.OK),
        ('users:login', None, 'client', HTTPStatus.OK),
        ('users:signup', None, 'client', HTTPStatus.OK),
        ('news:edit', 'comment_id', 'author_client', HTTPStatus.OK),
        ('news:delete', 'comment_id', 'author_client', HTTPStatus.OK),
        ('news:edit', 'comment_id', 'reader_client', HTTPStatus.NOT_FOUND),
        ('news:delete', 'comment_id', 'reader_client', HTTPStatus.NOT_FOUND),
    ]
)
def test_pages_status(
    request, name, args, client_fixture,
    expected_status, news, comment
):
    client = request.getfixturevalue(client_fixture)
    if args == 'news_id':
        url = reverse(name, args=(news.id,))
    elif args == 'comment_id':
        url = reverse(name, args=(comment.id,))
    else:
        url = reverse(name)
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize('name', ['news:edit', 'news:delete'])
def test_redirects_for_anonymous(client, comment, name):
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f'{login_url}?next={url}'
