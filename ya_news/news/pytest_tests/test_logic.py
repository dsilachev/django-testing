from http import HTTPStatus

import pytest

from news.forms import WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


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


def test_author_can_delete_comment(author_client, comment_urls):
    response = author_client.delete(comment_urls['delete_url'])
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f"{comment_urls['news_url']}#comments"
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(
    reader_client, comment, comment_urls
):
    before = Comment.objects.get(pk=comment.pk)
    response = reader_client.delete(comment_urls['delete_url'])
    after = Comment.objects.get(pk=comment.pk)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
    assert after.text == before.text
    assert after.author == before.author
    assert after.news == before.news


def test_author_can_edit_comment(author_client, comment, comment_urls):
    new_data = {'text': 'Обновлённый комментарий'}
    before = Comment.objects.get(pk=comment.pk)
    response = author_client.post(comment_urls['edit_url'], data=new_data)
    after = Comment.objects.get(pk=comment.pk)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f"{comment_urls['news_url']}#comments"
    assert after.text == new_data['text']
    assert after.author == before.author
    assert after.news == before.news


def test_user_cant_edit_comment_of_another_user(
    reader_client, comment, comment_urls
):
    new_data = {'text': 'Обновлённый комментарий'}
    before = Comment.objects.get(pk=comment.pk)
    response = reader_client.post(comment_urls['edit_url'], data=new_data)
    after = Comment.objects.get(pk=comment.pk)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert after.text == before.text
    assert after.author == before.author
    assert after.news == before.news
