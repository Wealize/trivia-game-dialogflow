import os
import unittest

from middleware import is_token_valid


class MiddlewareTestCase(unittest.TestCase):
    def setUp(self):
        os.environ.setdefault('TOKEN', 'token')

    def test_is_token_valid_empty_token(self):
        is_valid = is_token_valid(None)

        self.assertFalse(is_valid)

    def test_is_token_valid_invalid_token(self):
        is_valid = is_token_valid('invalid_token')

        self.assertFalse(is_valid)

    def test_is_token_valid_return_true(self):
        is_valid = is_token_valid('token')

        self.assertTrue(is_valid)
