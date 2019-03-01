import unittest
from unittest.mock import patch
import os
import json

import dialogflow

from services import IntentsSyncronizer

class IntentSyncronizerTestCase(unittest.TestCase):
    @patch.object(IntentsSyncronizer, '__init__')
    def setUp(self, __init__):
        INTENT_PARENT = 'game'
        dialogflow_credentials_file = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        with open(dialogflow_credentials_file) as f:
            project_id = json.load(f).get('project_id')
        __init__.return_value = None

        self.service = IntentsSyncronizer(project_id, INTENT_PARENT)

    @patch.object(IntentsSyncronizer, 'get_intent_id')
    def test_get_intent_id(self, get_intent_id):
        get_intent_id.return_value = '1'

        id = self.service.get_intent_id('name')

        self.assertEqual(id, '1')

    def test_get_correct_response_messages(self):
        response = 'holi'
        expected_result = ['correcto, la respuesta correcta es holi ¿quieres seguir jugando?']

        result = self.service.get_correct_response_messages(response)

        self.assertEqual(result, expected_result)

    def test_get_incorrect_response_messages(self):
        response = 'holi'
        expected_result = ['incorrecto, la respuesta correcta es holi ¿quieres seguir jugando?']

        result = self.service.get_incorrect_response_messages(response)

        self.assertEqual(result, expected_result)

    def test_get_text_message(self):
        message_texts = ['ok', 'vale']
        expected_result = dialogflow.types.Intent.Message.Text(text=message_texts)

        result = self.service.get_text_message(message_texts)

        self.assertEqual(result, expected_result)

    def test_get_text_message_empty(self):
        message_texts = []
        expected_result = dialogflow.types.Intent.Message.Text(text=message_texts)
        result = self.service.get_text_message(message_texts)

        self.assertEqual(result, expected_result)

    def test_get_message(self):
        text = dialogflow.types.Intent.Message.Text(text=['holi'])
        expected_result = dialogflow.types.Intent.Message(text=text)

        result = self.service.get_message(text)

        self.assertEqual(result, expected_result)

    def test_get_message_empty(self):
        text = dialogflow.types.Intent.Message.Text(text=[])
        expected_result = dialogflow.types.Intent.Message(text=text)

        result = self.service.get_message(text)

        self.assertEqual(result, expected_result)

    def test_get_training_phrase_with_phrase(self):
        part = dialogflow.types.Intent.TrainingPhrase.Part(
                text='holi')
        expected_result= dialogflow.types.Intent.TrainingPhrase(parts=[part])

        result = self.service.get_training_phrase(part)

        self.assertEqual(result, expected_result)

    def test_get_training_phrase_empty(self):
        part = dialogflow.types.Intent.TrainingPhrase.Part(
                text='')
        expected_result= dialogflow.types.Intent.TrainingPhrase(parts=[part])

        result = self.service.get_training_phrase(part)

        self.assertEqual(result, expected_result)

    def test_get_training_phrases_with_parts(self):
        training_phrases_part = 'holi'
        part = dialogflow.types.Intent.TrainingPhrase.Part(
                text=training_phrases_part)
        expected_result=[dialogflow.types.Intent.TrainingPhrase(parts=[part])]

        result = self.service.get_training_phrases([training_phrases_part])

        self.assertEqual(result, expected_result )

