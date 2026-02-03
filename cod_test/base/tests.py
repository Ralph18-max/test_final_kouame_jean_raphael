from django.test import TestCase
from django.apps import apps


class BaseAppTests(TestCase):
    def test_base_app_is_installed(self):
        config = apps.get_app_config('base')
        self.assertEqual(config.name, 'base')

