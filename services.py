from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2 import service_account
import gspread
import dialogflow
import os

class SpreadsheetReader:
    def __init__(self, key, credentials_file):
        SCOPE = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, SCOPE)
        self.gspr = gspread.authorize(credentials)
        self.worksheet = self.get_first_sheet(key)

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
    def __init__(self, project_id, intent_parent):
        self.project_id = project_id
        self.intents_client = dialogflow.IntentsClient()
        self.parent = self.intents_client.project_agent_path(self.project_id)
        self.intent_parent = intent_parent
        self.default_user_expresion = ['si', 'claro', 'ok', 'vale', 'por supuesto', 'buena idea']

    def syncronize_intents(self, intents):
        self.delete_intents()
        self.create_intents(intents)

    def create_intents(self, intents):
        for intent in intents:
            self.create_intents_for_question(intent)

    # Create three intents for each question (question, correct response, incorrect response)
    def create_intents_for_question(self, intent):
        intent_parent_question_id = self.get_intent_id(self.intent_parent)
        question = intent[0]
        correct_response = ' '.join([intent[1], intent[2]])
        intent_name = Formatter.format_intent_name(question)
        contexts = self.get_contexts_for_intent(intent_name)

        self.create_question_intent(contexts, intent_parent_question_id, intent_name, question)
        intent_parent_response_id = self.get_intent_id(intent_name)
        self.create_correct_response(intent_parent_response_id, intent_name, contexts, correct_response)
        self.create_incorrect_response(intent_parent_response_id, intent_name, contexts, correct_response)

    def create_question_intent(self, contexts, intent_parent_question_id, intent_name, question):
        self.create_intent(intent_name, self.default_user_expresion,
            [question], intent_parent_question_id,
                contexts.get('input_contexts_question'),
                    contexts.get('output_contexts_question'))

    def create_correct_response(self, intent_parent_response_id, intent_name, contexts,
        correct_response):
        self.create_response(intent_parent_response_id, intent_name+'-yes', [correct_response],
            self.get_correct_response_messages(correct_response), contexts, correct_response)

    def create_incorrect_response(self, intent_parent_response_id, intent_name, contexts,
        correct_response):
        self.create_response(intent_parent_response_id, intent_name+'-no', [''],
            self.get_incorrect_response_messages(correct_response), contexts, correct_response)

    def create_response(self, intent_parent_response_id, intent_name, user_expresions, responses,
        contexts, correct_response):
        self.create_intent(intent_name, user_expresions, responses,
                intent_parent_response_id, contexts.get('input_contexts_response'))

    def get_correct_response_messages(self, response):
        return ['correcto, la respuesta correcta es {} ¿quieres seguir jugando?'.format(response)]

    def get_incorrect_response_messages(self, response):
        return  ['incorrecto, la respuesta correcta es {} ¿quieres seguir jugando?'.format(response)]

    def get_contexts_for_intent(self, intent_name):
        if not intent_name:
            raise Exception('The intent name is empty')
        return dict(
            [('output_contexts_question', [ self.get_context(self.intent_parent + "-yes-followup", 2),
                self.get_context(intent_name+"-followup", 2)]),
            ('input_contexts_question', [self.get_context_path(self.intent_parent)]),
            ('input_contexts_response', [self.get_context_path(self.intent_parent + "-yes-followup")])
            ])

    def get_context(self, context_name, lifespan_count=None):
        return dialogflow.types.Context(
                name=self.get_context_path(context_name),
                lifespan_count=lifespan_count)

    def get_context_path(self, context_name):
        contexts_client = dialogflow.ContextsClient()
        return contexts_client.context_path(self.project_id, "-", context_name)

    def create_intent(self, display_name, training_phrases_parts,
                  message_texts, intent_parent_id, input_contexts=None, output_contexts=None):
        intent = self.get_intent(display_name, training_phrases_parts,
                  message_texts, intent_parent_id, input_contexts, output_contexts)

        response = self.intents_client.create_intent(self.parent, intent)

        print('Intent created: {}'.format(response))

    def get_intent(self, display_name, training_phrases_parts,
                  message_texts, intent_parent_id, input_contexts=None, output_contexts=None):
        intent = dialogflow.types.Intent(
            display_name=display_name,
            training_phrases=self.get_training_phrases(training_phrases_parts),
            messages=[self.get_message(self.get_text_message(message_texts))],
            parent_followup_intent_name=self.get_parent_followup_intent_name(intent_parent_id),
            input_context_names=input_contexts,
            output_contexts=output_contexts)
        return intent

    def get_parent_followup_intent_name(self, intent_parent_id):
        return "projects/{}/agent/intents/{}".format(self.project_id, intent_parent_id)

    def get_text_message(self, message_texts):
        return dialogflow.types.Intent.Message.Text(text=message_texts)

    def get_message(self, text):
        return dialogflow.types.Intent.Message(text=text)

    def get_training_phrases(self, training_phrases_parts):
        training_phrases = []
        for training_phrases_part in training_phrases_parts:
            part = dialogflow.types.Intent.TrainingPhrase.Part(
                text=training_phrases_part)
            # Here we create a new training phrase for each provided part.
            training_phrase = self.get_training_phrase(part)
            training_phrases.append(training_phrase)
        return training_phrases

    def get_training_phrase(self, part):
        return dialogflow.types.Intent.TrainingPhrase(parts=[part])

    def delete_intents(self):
        intents = self.intents_client.list_intents(self.parent)
        for intent in intents:
            if self.is_game_intent(intent):
                self.delete_intent(intent)

    def is_game_intent(self, intent):
        contexts_client = dialogflow.ContextsClient()
        return contexts_client.context_path(self.project_id, "-",
            self.intent_parent) in intent.input_context_names

    def delete_intent(self, intent):
        intent_id = self.get_intent_id(intent.display_name)
        intent_path = self.intents_client.intent_path(self.project_id, intent_id)
        self.intents_client.delete_intent(intent_path)

    def get_intent_id(self, display_name):
        intents = self.intents_client.list_intents(self.parent)
        intent_names = [
            intent.name for intent in intents
            if intent.display_name == display_name]

        intent_ids = [
            intent_name.split('/')[-1] for intent_name
            in intent_names]

        return intent_ids[0]

class Formatter():
    @staticmethod
    def format_intent_name(question):
        question = question.replace(" ", "")
        incorrect_letters,correct_letters = 'áéíóúü','aeiouu'
        trans = str.maketrans(incorrect_letters,correct_letters)
        return question.translate(trans)
