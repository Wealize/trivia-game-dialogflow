import os
import json
import random

import gspread
import redis
import dialogflow
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2 import service_account
from slugify import slugify


class PersistService:
    QUESTIONS_KEY = 'abc:questions'

    def __init__(self, url, db=0):
        self.client = redis.from_url(url)

    def set_questions(self, data):
        self.client.set(self.QUESTIONS_KEY, json.dumps(data))

    def get_questions(self):
        try:
            return json.loads(self.client.get(self.QUESTIONS_KEY))
        except json.JSONDecodeError:
            return []


class QuestionService:
    def __init__(self, questions):
        self.questions = questions

    def get_question(self):
        return random.choice(self.questions)


class SpreadsheetReader:
    def __init__(self, spreadsheet_id, credentials):
        SCOPE = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            credentials, SCOPE
        )
        self.gspr = gspread.authorize(credentials)
        self.worksheet = self.get_first_sheet(spreadsheet_id)

    def get_first_sheet(self, key):
        spreadsheet = self.open_sheet(key)
        return spreadsheet.sheet1

    def open_sheet(self, key):
        return self.gspr.open_by_key(key)

    def get_values_from_sheet(self):
        values_list = self.worksheet.get_all_values()
        values_list.pop(0)
        return values_list


class IntentsSyncronizer:
    CORRECT_MESSAGE = 'correcto, la respuesta correcta es {} ¿quieres seguir jugando?'
    INCORRECT_MESSAGE = 'incorrecto, la respuesta correcta es {} ¿quieres seguir jugando?'

    def __init__(self, dialogflow_creds, intent_parent_name):
        self.project_id = dialogflow_creds['project_id']
        self.credentials = service_account.Credentials.from_service_account_info(
            dialogflow_creds)
        self.intents_client = dialogflow.IntentsClient(
            credentials=self.credentials)
        self.contexts_client = dialogflow.ContextsClient(
            credentials=self.credentials)
        self.parent = self.intents_client.project_agent_path(self.project_id)
        self.intent_parent = intent_parent_name

    def syncronize_intents(self, intents):
        self.delete_intents()
        self.create_intents(intents)

    def create_intents(self, intents):
        for intent in intents:
            self.create_intents_for_question(intent)

    def create_intents_for_question(self, intent):
        intent_parent_question_id = self.get_intent_id(self.intent_parent)
        question = intent[0]
        correct_response = ' '.join([intent[1], intent[2]])
        intent_name = slugify(question, to_lower=True)
        contexts = self.get_contexts_for_intent(intent_name)

        # Question intent
        question_intent = self.create_intent(
            intent_name,
            [question],
            [question],
            intent_parent_question_id,
            contexts.get('input_contexts_question'),
            contexts.get('output_contexts_question'))

        intent_parent_response_id = question_intent.name.split('/')[-1]

        self.create_response(
            intent_parent_response_id,
            '{}-yes'.format(intent_name),
            [correct_response],
            [self.CORRECT_MESSAGE.format(correct_response)],
            contexts,
            correct_response)
        self.create_response(
            intent_parent_response_id,
            '{}-no'.format(intent_name),
            [''],
            [self.INCORRECT_MESSAGE.format(correct_response)],
            contexts,
            correct_response)

    def create_response(
            self,
            intent_parent_response_id,
            intent_name,
            user_expresions,
            responses,
            contexts,
            correct_response):
        self.create_intent(intent_name, user_expresions, responses,
                           intent_parent_response_id, contexts.get('input_contexts_response'))

    def get_contexts_for_intent(self, intent_name):
        if not intent_name:
            raise Exception('The intent name is empty')
        return dict(
            [('output_contexts_question', [self.get_context(self.intent_parent + "-yes-followup", 2),
                                           self.get_context(intent_name+"-followup", 2)]),
             ('input_contexts_question', [
              self.get_context_path(self.intent_parent)]),
             ('input_contexts_response', [self.get_context_path(
                 self.intent_parent + "-yes-followup")])
             ])

    def get_context(self, context_name, lifespan_count=None):
        return dialogflow.types.Context(
            name=self.get_context_path(context_name),
            lifespan_count=lifespan_count)

    def get_context_path(self, context_name):
        return self.contexts_client.context_path(self.project_id, "-", context_name)

    def create_intent(self, display_name, training_phrases_parts,
                      message_texts, intent_parent_id, input_contexts=None, output_contexts=None):
        intent = dialogflow.types.Intent(
            display_name=display_name,
            training_phrases=self.get_training_phrases(training_phrases_parts),
            messages=[
                dialogflow.types.Intent.Message(
                    text=dialogflow.types.Intent.Message.Text(text=message_texts)
                )
            ],
            parent_followup_intent_name="projects/{}/agent/intents/{}".format(
                self.project_id, intent_parent_id
            ),
            input_context_names=input_contexts,
            output_contexts=output_contexts)

        return self.intents_client.create_intent(self.parent, intent)

    def get_training_phrases(self, training_phrases_parts):
        training_phrases = []
        for training_phrases_part in training_phrases_parts:
            part = dialogflow.types.Intent.TrainingPhrase.Part(
                text=training_phrases_part)
            training_phrase = dialogflow.types.Intent.TrainingPhrase(parts=[part])
            training_phrases.append(training_phrase)
        return training_phrases

    def delete_intents(self):
        intents = self.intents_client.list_intents(self.parent)
        for intent in intents:
            if self.is_game_intent(intent):
                self.delete_intent(intent)

    def is_game_intent(self, intent):
        return self.contexts_client.context_path(
            self.project_id, "-", self.intent_parent
        ) in intent.input_context_names

    def delete_intent(self, intent):
        intent_id = intent.name.split('/')[-1]
        intent_path = self.intents_client.intent_path(self.project_id, intent_id)
        self.intents_client.delete_intent(intent_path)

    def get_intent_id(self, display_name):
        intents = self.intents_client.list_intents(self.parent)
        intent_ids = [
            intent.name.split('/')[-1]
            for intent in intents
            if intent.display_name == display_name]

        return intent_ids[0]
