import json
import os
import django

from datetime import datetime, timedelta

import requests
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from mail_api.models import Mail, Client

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mailinglist.settings")
django.setup()


class TestMailViewSet(APITestCase):

    def authenticate(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'secret'
        }
        user = User.objects.create_user(**self.credentials)
        self.client.force_login(user)

    def create_mail(self):
        c = Client.objects.create(mobile="79112345678", timezone='Africa/Dakar')
        sample_mail = {
            'id': 1,
            'text': "This is a sample test text",
            'start_at': datetime.now(),
            'stop_at': datetime.now() + timedelta(minutes=30),
            'schedule': '* */3 * * *',
            'clients': c.pk
        }

        response = self.client.post(reverse('mail-list'), sample_mail)

        return response

    def test_should_not_create_mail_with_no_auth(self):
        response = self.create_mail()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_should_create_mail(self):
        previous_mail_count = Mail.objects.all().count()
        self.authenticate()
        response = self.create_mail()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(Mail.objects.all().count(), previous_mail_count)
        self.assertEqual(response.data['text'], "This is a sample test text")

    def test_retrieve_all_mails(self):
        self.authenticate()
        res = self.client.get(reverse('mail-list'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsInstance(res.data['results'], list)

        self.create_mail()
        res = self.client.get(reverse('mail-list'))
        self.assertIsInstance(res.data['count'], int)
        self.assertEqual(res.data['count'], 1)

    def test_retrieves_one_item(self):
        self.authenticate()
        response = self.create_mail()

        res = self.client.get(reverse('mail-detail', kwargs={'pk': response.data['id']}))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        mail = Mail.objects.get(id=response.data['id'])
        self.assertEqual(mail.text, res.data['text'])

    def test_deletes_one_item(self):
        self.authenticate()
        res = self.create_mail()
        prev_db_count = Mail.objects.all().count()

        self.assertGreater(prev_db_count, 0)
        self.assertEqual(prev_db_count, 1)

        response = self.client.delete(
            reverse("mail-detail", kwargs={'pk': res.data['id']}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Mail.objects.all().count(), 0)


class ExternalApiTests(APITestCase):

    def test_post_external_API(self):
        token = os.getenv('EXTERNAL_API_TOKEN')
        msg_id = 3

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        data = {
            'id': msg_id,
            'phone': int("79112345678"),
            'text': 'Sample text',
        }

        res = requests.post(f'{os.getenv("EXTERNAL_URL")}/{msg_id}', headers=headers, data=json.dumps(data))

        print(res.status_code)
        print(res.json(), '\nОчередное сообщение отправлено!')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_check_mail_status(self):
        mails = Mail.objects.all()

        if mails:
            for mail in mails:
                if timezone.now() > mail.stop_at:
                    mail.status = "outdated"
                    self.assertEqual(mail.status, "outdated")
                else:
                    if timezone.now() > mail.start_at:
                        mail.status = "active"
                        self.assertEqual(mail.status, "active")
                    else:
                        mail.status = "future"
                        self.assertEqual(mail.status, "future")
        else:
            return "Не создана ни одна рассылка."

        return "Статусы рассылок успешно обновлены"
