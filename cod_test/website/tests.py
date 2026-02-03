from django.test import TestCase
from django.urls import reverse, resolve


class WebsiteUrlsTests(TestCase):
    def test_index_url_resolves(self):
        url = reverse('index')
        match = resolve(url)
        self.assertEqual(match.view_name, 'index')

    def test_about_url_resolves(self):
        url = reverse('about')
        match = resolve(url)
        self.assertEqual(match.view_name, 'about')


class WebsiteSmokeTests(TestCase):
    def test_index_returns_200(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_about_returns_200(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
