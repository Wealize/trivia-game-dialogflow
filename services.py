import os
import json
import random

import gspread
import redis
from oauth2client.service_account import ServiceAccountCredentials
from slugify import slugify


class QuestionStateService:
    CONTEXT_PATTERN = 'projects/{}/agent/sessions/{}/contexts/{}'
    SOURCE = 'abc.theneonproject.org'

    STATE_SEND_QUESTION = 'send_question'
    STATE_ANSWER_QUESTION = 'answer_question'
    STATE_FINISH_GAME = 'finish_game'

    def __init__(self, project_id, session, contexts, questions, text):
        self.project_id = project_id
        self.session = session
        self.contexts = contexts
        self.questions = questions
        self.text = text
        self.question_service = QuestionService(self.session, self.questions)

    def get_next_state_from_context(self):
        if self.text in self.question_service.FINISH_GAME_SENTENCES:
            return self.STATE_FINISH_GAME

        has_question = self.is_question_context_present()

        if has_question:
            return self.STATE_ANSWER_QUESTION

        return self.STATE_SEND_QUESTION

    def is_question_context_present(self):
        return next(
            (context for context in self.contexts
             if context['name'] == self.get_context_path('question')),
            None
        )

    def get_next_response_from_request(self, next_state):
        response = self.question_service.FINISH_GAME_RESPONSE

        if next_state == self.STATE_ANSWER_QUESTION:
            current_question = self.get_question_from_context()
            return self.question_service.get_response_to_question(
                self.text, current_question)

        elif next_state == self.STATE_SEND_QUESTION:
            next_question = self.question_service.get_question(
                self.get_questions_history())
            response = next_question['text']

        return response

    def get_next_context_from_request(self, next_state, next_question_context=None):
        question_context = self.get_context_path('question')
        game_context = self.get_context_path('game')
        gamefollowup_context = self.get_context_path('game-followup')
        output_contexts = []

        if next_state == self.STATE_ANSWER_QUESTION:
            output_contexts = [
                {
                    "name": game_context,
                    "lifespanCount": 1,
                    "parameters": {}
                },
                {
                    "name": gamefollowup_context,
                    "lifespanCount": 1,
                    "parameters": {}
                },
            ]
        elif next_state == self.STATE_SEND_QUESTION:
            history_context = self.get_context_path('question_history')
            next_question_context = slugify(
                next_question_context, to_lower=True)
            questions_history = self.get_questions_history() + [next_question_context]

            output_contexts = [
                {
                    "name": game_context,
                    "lifespanCount": 1,
                    "parameters": {}
                },
                {
                    "name": gamefollowup_context,
                    "lifespanCount": 1,
                    "parameters": {}
                },
                {
                    "name": question_context,
                    "lifespanCount": 1,
                    "parameters": {
                        'question': next_question_context
                    }
                },
                {
                    "name": history_context,
                    "lifespanCount": 5,
                    "parameters": {
                        'questions': questions_history
                    }
                }
            ]

        return output_contexts

    def get_questions_history(self):
        question_history_context_path = self.get_context_path(
            'question_history')
        questions_history = next(
            (context['parameters']['questions'] for context in self.contexts
             if context['name'] == question_history_context_path),
            None
        )

        return questions_history or []

    def get_next_response(self):
        next_state = self.get_next_state_from_context()
        next_response = self.get_next_response_from_request(next_state)
        next_contexts = self.get_next_context_from_request(
            next_state, next_response)

        return self.get_dialogflow_response(next_response, next_contexts)

    def get_question_from_context(self):
        question_context_path = self.get_context_path('question')
        question_context = next(
            (context['parameters']['question'] for context in self.contexts
             if context['name'] == question_context_path),
            None
        )

        return next(
            (question for question in self.questions
             if question['context'] == question_context),
            None
        )

    def get_dialogflow_response(self, response, contexts):
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
                                    'textToSpeech': response
                                }
                            }
                        ]
                    }
                }
            },
            'outputContexts': contexts
        }

    def get_context_path(self, name):
        return self.CONTEXT_PATTERN.format(self.project_id, self.session, name)


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
    CORRECT_QUESTION_FORMAT = 'Correcto! , {} {} ¿Quieres volver a jugar?'
    INCORRECT_QUESTION_FORMAT = 'Incorrecto, la respuesta correcta es: {}, ¿Quieres volver a jugar?'
    FINISH_GAME_SENTENCES = ['no', 'cancelar']
    FINISH_GAME_RESPONSE = 'Muchas gracias por jugar!'
    MINIMUM_TEXT_CHARS_RESPONSE = 3

    def __init__(self, session_id, questions):
        self.session_id = session_id
        self.questions = questions

    def get_question(self, questions_history):
        questions = list(filter(
            lambda question: question['context'] not in questions_history,
            self.questions
        ))
        return random.choice(questions)

    def get_response_to_question(self, text, question_object):
        response = self.INCORRECT_QUESTION_FORMAT.format(
            question_object['correct_response'])

        if self.is_valid_answer(text, question_object['correct_response']):
            response = self.CORRECT_QUESTION_FORMAT.format(
                question_object['correct_response'],
                question_object['description']
            )

        return response

    def is_valid_answer(self, text, correct_response):
        return len(text) > self.MINIMUM_TEXT_CHARS_RESPONSE and \
            text in correct_response.lower()


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
