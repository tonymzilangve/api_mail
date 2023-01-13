import os
import django

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from mail_api.models import Mail, Client, Tag

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mailinglist.settings")
django.setup()


class TestClientViewSet(APITestCase):

    def authenticate(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'secret'
        }
        user = User.objects.create_user(**self.credentials)
        self.client.force_login(user)

    def create_client(self):
        sample_client = {
            'mobile': "79112345678",
            'timezone': 'Africa/Dakar'
        }
        response = self.client.post(reverse('client-list'), sample_client)
        return response

    def test_should_not_create_client_with_no_auth(self):
        response = self.create_client()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_should_create_client(self):
        previous_client_count = Client.objects.all().count()
        self.authenticate()
        response = self.create_client()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(Client.objects.all().count(), previous_client_count)
        self.assertEqual(response.data['mobile'], "79112345678")
        self.assertEqual(response.data['timezone'], 'Africa/Dakar')

    def test_retrieve_all_clients(self):
        self.authenticate()
        res = self.client.get(reverse('client-list'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsInstance(res.data['results'], list)

        self.create_client()
        res = self.client.get(reverse('client-list'))
        self.assertIsInstance(res.data['count'], int)
        self.assertEqual(res.data['count'], 1)

    def test_retrieves_one_item(self):
        self.authenticate()
        response = self.create_client()

        res = self.client.get(reverse('client-detail', kwargs={'pk': response.data['id']}))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        client = Client.objects.get(id=response.data['id'])
        self.assertEqual(client.mobile, res.data['mobile'])

    def test_deletes_one_item(self):
        self.authenticate()
        res = self.create_client()
        prev_db_count = Client.objects.all().count()

        self.assertGreater(prev_db_count, 0)
        self.assertEqual(prev_db_count, 1)

        response = self.client.delete(
            reverse("client-detail", kwargs={'pk': res.data['id']}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Client.objects.all().count(), 0)


class TestTagViewSet(APITestCase):

    def authenticate(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'secret'
        }
        user = User.objects.create_user(**self.credentials)
        self.client.force_login(user)

    def create_tag(self):
        sample_tag = {
            'name': 'sample tag'
        }
        response = self.client.post(reverse('tag-list'), sample_tag)
        return response

    def test_should_not_create_tag_with_no_auth(self):
        response = self.create_tag()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_should_create_tag(self):
        previous_tag_count = Tag.objects.all().count()
        self.authenticate()
        response = self.create_tag()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertGreater(Tag.objects.all().count(), previous_tag_count)
        self.assertEqual(response.data['name'], "sample tag")

    def test_retrieve_all_tags(self):
        self.authenticate()
        res = self.client.get(reverse('tag-list'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsInstance(res.data['results'], list)

        self.create_tag()
        res = self.client.get(reverse('tag-list'))
        self.assertIsInstance(res.data['count'], int)
        self.assertEqual(res.data['count'], 1)

    def test_retrieves_one_item(self):
        self.authenticate()
        response = self.create_tag()

        res = self.client.get(reverse('tag-detail', kwargs={'pk': response.data['id']}))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        tag = Tag.objects.get(id=response.data['id'])
        self.assertEqual(tag.name, res.data['name'])

    def test_updates_one_item(self):
        self.authenticate()
        response = self.create_tag()

        res = self.client.patch(reverse('tag-detail', kwargs={'pk': response.data['id']}), {'name': "New tag name"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        updated_tag = Tag.objects.get(id=response.data['id'])
        self.assertEqual(updated_tag.name, 'New tag name')

    def test_deletes_one_item(self):
        self.authenticate()
        res = self.create_tag()
        prev_db_count = Tag.objects.all().count()

        self.assertGreater(prev_db_count, 0)
        self.assertEqual(prev_db_count, 1)

        response = self.client.delete(
            reverse("tag-detail", kwargs={'pk': res.data['id']}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Tag.objects.all().count(), 0)
