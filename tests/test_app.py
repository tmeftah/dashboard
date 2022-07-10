from tests.basic import BasicsTestCase
from flask import current_app


class TestApp(BasicsTestCase):
    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config["TESTING"])
