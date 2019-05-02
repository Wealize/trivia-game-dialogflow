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
