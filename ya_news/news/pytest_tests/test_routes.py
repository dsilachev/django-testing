from http import HTTPStatus

import pytest
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    [
        ('news:home', None),
        ('news:detail', 'news_id'),
        ('users:login', None),
        ('users:signup', None),
    ]
)
def test_pages_availability(client, news, name, args):
    url_args = (news.id,) if args == 'news_id' else args
    url = reverse(name, args=url_args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'user_fixture, status',
    [
        ('author', HTTPStatus.OK),
        ('reader', HTTPStatus.NOT_FOUND),
    ]
)
@pytest.mark.parametrize('name', ['news:edit', 'news:delete'])
def test_availability_for_comment_edit_and_delete(
    client, comment, request, user_fixture, status, name
):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = reverse(name, args=(comment.id,))
    response = client.get(url)
    assert response.status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize('name', ['news:edit', 'news:delete'])
def test_redirect_for_anonymous_user(client, comment, name):
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id,))
    response = client.get(url)
    expected_redirect = f'{login_url}?next={url}'
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_redirect


@pytest.mark.django_db
def test_logout_availability(client, author):
    url = reverse('users:logout')
    client.force_login(author)
    response = client.post(url)
    assert response.status_code in [HTTPStatus.FOUND, HTTPStatus.OK]
    response = client.get(url)
    assert response.status_code in [HTTPStatus.OK, HTTPStatus.FOUND, 405]
