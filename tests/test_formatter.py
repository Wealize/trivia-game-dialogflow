import unittest

from services import Formatter


class FormatterTestCase(unittest.TestCase):
    def test_get_intent_name_with_latin_character(self):
        question = 'adiós'
        expected_result = 'adios'

        result = Formatter.format_intent_name(question)

        self.assertEqual(result, expected_result)

    def test_get_intent_name_without_latin_character(self):
        question = 'holi'
        expected_result = 'holi'

        result = Formatter.format_intent_name(question)

        self.assertEqual(result, expected_result)

    def test_get_intent_name_empty(self):
        question = ''
        expected_result = ''

        result = Formatter.format_intent_name(question)

        self.assertEqual(result, expected_result)
