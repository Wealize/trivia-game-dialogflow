import unittest
from unittest.mock import patch
import os

from services import SpreadsheetReader

class SpreadsheetReaderTestCase(unittest.TestCase):
    @patch.object(SpreadsheetReader, '__init__')
    def setUp(self, __init__):
        key = os.environ.get('KEY')
        credentials_file = os.environ.get('SHEET_CREDENTIALS_FILE')
        __init__.return_value = None

        self.service = SpreadsheetReader(key, credentials_file)

    @patch.object(SpreadsheetReader, 'get_values_from_sheet')
    def test_get_values_from_sheet(self, get_values_from_sheet):
        get_values_from_sheet.return_value = [
            [ 'pregunta', 'respuesta']
        ]

        values_sheet = self.service.get_values_from_sheet()

        self.assertEqual(len(values_sheet), 1)
