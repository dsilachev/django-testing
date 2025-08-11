from http import HTTPStatus

import pytest

from news.forms import WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db

NEW_DATA = {'text': 'Обновлённый комментарий'}


def test_anonymous_user_cant_create_comment(
    client, news_detail_url, form_data
):
    client.post(news_detail_url, data=form_data)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
    author_client, news_detail_url, form_data, news, author
):
    response = author_client.post(news_detail_url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f'{news_detail_url}#comments'
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(
    author_client, news_detail_url, bad_words_data
):
    response = author_client.post(news_detail_url, data=bad_words_data)
    form = response.context['form']
    assert form.errors
    assert WARNING in form.errors['text']
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(
    author_client, comment_delete_url, news_detail_url
):
    response = author_client.delete(comment_delete_url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f"{news_detail_url}#comments"
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(
    reader_client, comment, comment_delete_url
):
    response = reader_client.delete(comment_delete_url)
    comment.refresh_from_db()
    after = Comment.objects.get(pk=comment.pk)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
    assert after.text == comment.text
    assert after.author == comment.author
    assert after.news == comment.news


def test_author_can_edit_comment(
    author_client, comment, comment_edit_url, news_detail_url
):
    response = author_client.post(comment_edit_url, data=NEW_DATA)
    comment.refresh_from_db()
    after = Comment.objects.get(pk=comment.pk)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f"{news_detail_url}#comments"
    assert after.text == NEW_DATA['text']
    assert after.author == comment.author
    assert after.news == comment.news


def test_user_cant_edit_comment_of_another_user(
    reader_client, comment, comment_edit_url
):
    response = reader_client.post(comment_edit_url, data=NEW_DATA)
    comment.refresh_from_db()
    after = Comment.objects.get(pk=comment.pk)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert after.text == comment.text
    assert after.author == comment.author
    assert after.news == comment.news
