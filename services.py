import os
import json
import random

import gspread
import redis
from oauth2client.service_account import ServiceAccountCredentials
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
    CONTEXT_PATTERN = 'projects/{}/agent/sessions/{}/contexts/{}'
    CORRECT_QUESTION_FORMAT = 'Correcto! , {} {} ¿Quieres volver a jugar?'
    INCORRECT_QUESTION_FORMAT = 'Incorrecto, la respuesta correcta es: {}, ¿Quieres volver a jugar?'
    FINISH_GAME_SENTENCES = ['no']
    FINISH_GAME_RESPONSE = 'Muchas gracias por jugar!'
    SOURCE = 'abc.theneonproject.org'
    MINIMUM_TEXT_CHARS_RESPONSE = 3

    def __init__(self, project_id, session_id, questions):
        self.project_id = project_id
        self.session_id = session_id
        self.questions = questions

    def get_question(self):
        return random.choice(self.questions)

    def get_context(self, name):
        return self.CONTEXT_PATTERN.format(
            self.project_id,
            self.session_id,
            name
        )

    def get_question_from_context(self, contexts, new_context):
        question_context = next(
            (context['parameters']['question'] for context in contexts
             if context['name'] == new_context),
            None
        )

        return next(
            (question for question in self.questions
             if question['context'] == question_context),
            None
        )

    def get_response_to_question(self, text, question_object):
        response = self.INCORRECT_QUESTION_FORMAT.format(
            question_object['correct_response'])

        if len(text) > self.MINIMUM_TEXT_CHARS_RESPONSE and \
           text in question_object['correct_response']:
            response = self.CORRECT_QUESTION_FORMAT.format(
                question_object['correct_response'],
                question_object['description']
            )

        return response

    def get_dialogflow_response(self, response, question, contexts):
        return {
            'fulfillmentText': response,
            'fulfillmentMessages': [
                {
                    'text': {
                        'text': [response]
                    }
                }
            ],
            'source': self.SOURCE,
            'payload': {
                'google': {
                    'expectUserResponse': True,
                    'richResponse': {
                        'items': [
                            {
                                'simpleResponse': {
                                    'textToSpeech': question['text']
                                }
                            }
                        ]
                    }
                }
            },
            'outputContexts': contexts
        }


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
        return [
            {
                'text': question[0],
                'context': slugify(question[0], to_lower=True),
                'correct_response': question[1],
                'description': question[2]
            }
            for question in values_list
        ]
