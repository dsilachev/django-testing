from http import HTTPStatus
from django.urls import reverse

from .base import BaseTestCase


class TestRoutes(BaseTestCase):

    def test_availability_for_pages(self):
        urls = [
            (self.NOTES_HOME_URL, self.anonymous_client, HTTPStatus.OK),
            (self.USERS_LOGIN_URL, self.anonymous_client, HTTPStatus.OK),
            (self.USERS_SIGNUP_URL, self.anonymous_client, HTTPStatus.OK),

            (self.NOTES_ADD_URL, self.not_author_client, HTTPStatus.OK),
            (self.NOTES_LIST_URL, self.not_author_client, HTTPStatus.OK),
            (self.NOTES_SUCCESS_URL, self.not_author_client, HTTPStatus.OK),

            (self.NOTES_DETAIL_URL, self.author_client, HTTPStatus.OK),
            (self.NOTES_EDIT_URL, self.author_client, HTTPStatus.OK),
            (self.NOTES_DELETE_URL, self.author_client, HTTPStatus.OK),

            (
                self.NOTES_DETAIL_URL,
                self.not_author_client,
                HTTPStatus.NOT_FOUND
            ),
            (
                self.NOTES_EDIT_URL,
                self.not_author_client,
                HTTPStatus.NOT_FOUND
            ),
            (
                self.NOTES_DELETE_URL,
                self.not_author_client,
                HTTPStatus.NOT_FOUND
            ),

            (self.NOTES_ADD_URL, self.anonymous_client, HTTPStatus.FOUND),
            (self.NOTES_LIST_URL, self.anonymous_client, HTTPStatus.FOUND),
            (self.NOTES_SUCCESS_URL, self.anonymous_client, HTTPStatus.FOUND),
            (self.NOTES_DETAIL_URL, self.anonymous_client, HTTPStatus.FOUND),
            (self.NOTES_EDIT_URL, self.anonymous_client, HTTPStatus.FOUND),
            (self.NOTES_DELETE_URL, self.anonymous_client, HTTPStatus.FOUND),
        ]

        for url, client, expected_status in urls:
            with self.subTest(url=url, client=client):
                response = client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_redirects_for_anonymous_user(self):
        protected_urls = [
            self.NOTES_DETAIL_URL,
            self.NOTES_EDIT_URL,
            self.NOTES_DELETE_URL,
            self.NOTES_ADD_URL,
            self.NOTES_SUCCESS_URL,
            self.NOTES_LIST_URL,
        ]
        login_url = reverse('users:login')
        for url in protected_urls:
            with self.subTest(url=url):
                expected_redirect = f'{login_url}?next={url}'
                response = self.anonymous_client.get(url)
                self.assertRedirects(response, expected_redirect)
