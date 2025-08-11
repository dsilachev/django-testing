from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_lazyfixture import lazy_fixture

pytestmark = pytest.mark.django_db

NEWS_HOME_URL = lazy_fixture('home_url')
NEWS_DETAIL_URL = lazy_fixture('news_detail_url')
COMMENT_EDIT_URL = lazy_fixture('comment_edit_url')
COMMENT_DELETE_URL = lazy_fixture('comment_delete_url')
USERS_LOGIN_URL = lazy_fixture('users_login_url')
USERS_SIGNUP_URL = lazy_fixture('users_signup_url')


@pytest.mark.parametrize(
    'url, client_fixture, expected_status',
    [
        (NEWS_HOME_URL, 'client', HTTPStatus.OK),
        (NEWS_DETAIL_URL, 'client', HTTPStatus.OK),
        (USERS_LOGIN_URL, 'client', HTTPStatus.OK),
        (USERS_SIGNUP_URL, 'client', HTTPStatus.OK),
        (COMMENT_EDIT_URL, 'author_client', HTTPStatus.OK),
        (COMMENT_DELETE_URL, 'author_client', HTTPStatus.OK),
        (COMMENT_EDIT_URL, 'reader_client', HTTPStatus.NOT_FOUND),
        (COMMENT_DELETE_URL, 'reader_client', HTTPStatus.NOT_FOUND),
    ]
)
def test_pages_status(request, url, client_fixture, expected_status):
    client = request.getfixturevalue(client_fixture)
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize('name', ['news:edit', 'news:delete'])
def test_redirects_for_anonymous(client, comment, name):
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f'{login_url}?next={url}'
