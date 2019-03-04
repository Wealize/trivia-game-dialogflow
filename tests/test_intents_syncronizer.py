import unittest
from unittest.mock import patch
import os
import json

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

    @patch.object(IntentsSyncronizer, 'get_text_message')
    def test_get_text_message(self, get_text_message):
        message_texts = ['ok', 'vale']
        get_text_message.return_value = 'message'

        result = self.service.get_text_message(message_texts)

        self.assertEqual(result, 'message')

    @patch.object(IntentsSyncronizer, 'get_text_message')
    def test_get_text_message_empty(self, get_text_message):
        message_texts = []
        get_text_message.return_value = ''

        result = self.service.get_text_message(message_texts)

        self.assertEqual(result, '')

    @patch.object(IntentsSyncronizer, 'get_message')
    def test_get_message(self, get_message):
        text = 'holi'
        get_message.return_value = 'message'

        result = self.service.get_message(text)

        self.assertEqual(result, 'message')

    @patch.object(IntentsSyncronizer, 'get_message')
    def test_get_message_empty(self, get_message):
        text = ''
        get_message.return_value = 'message'

        result = self.service.get_message(text)

        self.assertEqual(result, 'message')

    @patch.object(IntentsSyncronizer, 'get_training_phrase')
    def test_get_training_phrase_with_phrase(self, get_training_phrase):
        part = 'holi'
        get_training_phrase.return_value = 'message'

        result = self.service.get_training_phrase(part)

        self.assertEqual(result, 'message')

    @patch.object(IntentsSyncronizer, 'get_training_phrase')
    def test_get_training_phrase_empty(self, get_training_phrase):
        part = ''
        get_training_phrase.return_value = 'message'

        result = self.service.get_training_phrase(part)

        self.assertEqual(result, 'message')

    @patch.object(IntentsSyncronizer, 'get_training_phrases')
    def test_get_training_phrases_with_parts(self, get_training_phrases):
        training_phrases_part = ['holi']
        get_training_phrases.return_value = ['holi']

        result = self.service.get_training_phrases(training_phrases_part)

        self.assertEqual(len(result), 1)

    @patch.object(IntentsSyncronizer, 'get_context')
    def test_get_context_when_receive_an_param(self, get_context):
        context_name = 'holi'
        get_context.return_value = 'context'

        result = self.service.get_context(context_name)

        self.assertEqual(result, 'context')

    @patch.object(IntentsSyncronizer, 'get_contexts_for_intent')
    def test_get_contexts_for_intent(self, get_contexts_for_intent):
        intent_name = 'holi'
        get_contexts_for_intent.return_value = dict(
            [('output_contexts_question', ''),
            ('input_contexts_question', ''),
            ('input_contexts_response', '')
            ])

        result = self.service.get_contexts_for_intent(intent_name)

        self.assertEqual(result, get_contexts_for_intent.return_value)

    def test_get_contexts_for_intent_when_intent_name_is_empty(self):
        intent_name = ''

        with self.assertRaises(Exception):
            self.service.get_contexts_for_intent(intent_name)

    @patch.object(IntentsSyncronizer, 'get_context_path')
    def test_get_context_path(self, get_context_path):
        context_name = 'holi'
        get_context_path.return_value = 'context_path'

        result = self.service.get_context_path(context_name)

        self.assertEqual(result, get_context_path.return_value)

    @patch.object(IntentsSyncronizer, 'get_intent')
    def test_get_intent(self, get_intent):
        get_intent.return_value = 'intent'

        result = self.service.get_intent(self, 'display_name', ['training_phrases_parts'],
                  ['message_texts'], 'intent_parent_id')

        self.assertEqual(result, get_intent.return_value)

    @patch.object(IntentsSyncronizer, 'get_parent_followup_intent_name')
    def test_get_parent_followup_intent_name(self, get_parent_followup_intent_name):
        get_parent_followup_intent_name.return_value = "projects/{}/agent/intents/{}".format(1, 1)

        result = self.service.get_parent_followup_intent_name('1')

        self.assertEqual(result, get_parent_followup_intent_name.return_value)

    @patch.object(IntentsSyncronizer, 'is_game_intent')
    def test_is_game_intent(self, is_game_intent):
        is_game_intent.return_value = True

        result = self.service.is_game_intent('game')

        self.assertTrue(result)


