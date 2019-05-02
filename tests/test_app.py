import unittest
from unittest.mock import patch
import os

from services import PersistService, SpreadsheetReader


class AppTestCase(unittest.TestCase):

    @patch.object(PersistService, '__init__')
    def setUp(self, persist_init):
        persist_init.return_value = None

        os.environ.setdefault('TOKEN', 'token')
        os.environ.setdefault('SPREADSHEET_CREDENTIALS', '{}')
        from app import app

        self.client = app.test_client()

    def test_sync_anonymous(self):

        result = self.client.get('/sync')

        self.assertEqual(result.status_code, 401)

    @patch.object(PersistService, 'set_questions')
    @patch.object(SpreadsheetReader, 'get_values_from_sheet')
    @patch.object(SpreadsheetReader, '__init__')
    def test_sync_authenticated(self, spread_init, values_from_sheet, set_questions):
        spread_init.return_value = None
        values_from_sheet.return_value = [['pregunta', 'respuesta']]
        set_questions.return_value = None

        result = self.client.get('/sync?token=token')

        self.assertEqual(result.status_code, 200)
