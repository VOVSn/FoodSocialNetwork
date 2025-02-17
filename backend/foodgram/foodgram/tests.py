from django.test import TestCase


class AlwaysSuccessTest(TestCase):
    def test_always_success(self):
        self.assertTrue(True)
