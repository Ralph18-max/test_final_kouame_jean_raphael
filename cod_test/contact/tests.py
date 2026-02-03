from django.test import TestCase
from django.urls import reverse, resolve
import json


class ContactUrlsTests(TestCase):
    def test_contact_url_resolves(self):
        url = reverse('contact')
        match = resolve(url)
        self.assertEqual(match.view_name, 'contact')

    def test_post_contact_url_resolves(self):
        url = reverse('post_contact')
        match = resolve(url)
        self.assertEqual(match.view_name, 'post_contact')

    def test_post_newsletter_url_resolves(self):
        url = reverse('post_newsletter')
        match = resolve(url)
        self.assertEqual(match.view_name, 'post_newsletter')


class ContactViewsTests(TestCase):
    def test_contact_page_returns_200(self):
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)

    def test_post_contact_returns_success_true_for_valid_payload(self):
        payload = {
            'email': 'test@example.com',
            'sujet': 'Sujet',
            'messages': 'Message',
            'nom': 'Nom',
        }
        response = self.client.post(
            reverse('post_contact'),
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('success', data)
        self.assertTrue(data['success'])

    def test_post_newsletter_returns_success_false_for_invalid_email(self):
        payload = {
            'email': 'not-an-email',
        }
        response = self.client.post(
            reverse('post_newsletter'),
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('success', data)
        self.assertFalse(data['success'])
