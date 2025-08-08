from http import HTTPStatus

import pytest
from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news):
    url = reverse('news:detail', args=(news.id,))
    form_data = {'text': 'Текст комментария'}
    client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_can_create_comment(client, news, author):
    url = reverse('news:detail', args=(news.id,))
    form_data = {'text': 'Текст комментария'}

    client.force_login(author)
    response = client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f'{url}#comments'
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == 'Текст комментария'
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(client, news, author):
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    client.force_login(author)
    response = client.post(url, data=bad_words_data)
    form = response.context['form']
    assert form.errors
    assert WARNING in form.errors['text']
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_author_can_delete_comment(client, comment):
    news_url = reverse('news:detail', args=(comment.news.id,))
    url_to_comments = news_url + '#comments'
    delete_url = reverse('news:delete', args=(comment.id,))
    client.force_login(comment.author)
    response = client.delete(delete_url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == url_to_comments
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(client, comment, reader):
    delete_url = reverse('news:delete', args=(comment.id,))
    client.force_login(reader)
    response = client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.django_db
def test_author_can_edit_comment(client, comment):
    news_url = reverse('news:detail', args=(comment.news.id,))
    url_to_comments = news_url + '#comments'
    edit_url = reverse('news:edit', args=(comment.id,))
    form_data = {'text': 'Обновлённый комментарий'}
    client.force_login(comment.author)
    response = client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == url_to_comments
    comment.refresh_from_db()
    assert comment.text == 'Обновлённый комментарий'


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(client, comment, reader):
    edit_url = reverse('news:edit', args=(comment.id,))
    form_data = {'text': 'Обновлённый комментарий'}
    original_text = comment.text
    client.force_login(reader)
    response = client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == original_text
