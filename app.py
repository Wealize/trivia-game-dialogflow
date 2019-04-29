import os
import json
from functools import wraps

from flask import Flask, request, jsonify, g
from werkzeug.exceptions import Unauthorized
from slugify import slugify

from services import (QuestionService, PersistService,
                      SpreadsheetReader, IntentsSyncronizer)

INTENT_PARENT = 'game'
TOKEN = os.environ.get('TOKEN')
app = Flask(__name__)
persist_service = PersistService(os.environ.get('REDIS_URL'))
intents_syncronizer = IntentsSyncronizer(
    json.loads(os.environ.get('DIALOGFLOW_CREDS')),
    INTENT_PARENT
)


def check_authentication(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.args.get('token')

        if not token or TOKEN != token:
            raise Unauthorized()

        return f(*args, **kwargs)
    return decorated_function


@app.route("/sync")
@check_authentication
def sync():
    spreadsheet_id = os.environ.get('SPREADSHEET_ID')
    credentials = json.loads(os.environ.get('SPREADSHEET_CREDENTIALS'))

    reader = SpreadsheetReader(spreadsheet_id, credentials)
    intents = reader.get_values_from_sheet()
    questions = [
        {'text': intent[0],
         'context': slugify(intent[0], to_lower=True),
         'correct_response': intent[1],
         'description': intent[2]
         }
        for intent in intents
    ]
    persist_service.set_questions(questions)
    # intents_syncronizer.syncronize_intents(intents)

    return "Sincronización completada con éxito"


@app.route("/hook", methods=['POST'])
@check_authentication
def webhook():
    request_dialogflow = request.get_json()
    print(request_dialogflow)
    session_id = request_dialogflow['session'].split('/')[-1]
    project_id = intents_syncronizer.project_id
    request_text = request_dialogflow['queryResult']['queryText']

    questions = persist_service.get_questions()
    question = QuestionService(questions).get_question()
    new_context = "projects/{}/agent/sessions/{}/contexts/{}".format(
        project_id, session_id, 'question')

    contexts = request_dialogflow['queryResult']['outputContexts']
    question_object = None

    for context in contexts:
        if context['name'] == new_context:
            question_context = context['parameters']['question']

            for question in questions:
                if question['context'] == question_context:
                    question_object = question

    if question_object:
        new_context = "projects/{}/agent/sessions/{}/contexts/{}".format(
            project_id, session_id, 'game')
        outputContexts = [
            {
                "name": new_context,
                "lifespanCount": 1,
                "parameters": {}
            }
        ]

        if request_text in question_object['correct_response']:
            response = ' '.join(
                [question_object['correct_response'], question_object['description']])
        else:
            response = 'Incorrecto, la respuesta correcta es: {}'.format(
                question_object['correct_response'])
    else:
        response = question['text']
        outputContexts = [
            {
                "name": new_context,
                "lifespanCount": 1,
                "parameters": {
                    'question': question['context']
                }
            }
        ]

    return jsonify(
        {
            "fulfillmentText": response,
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [response]
                    }
                }
            ],
            "source": "abc.theneonproject.org",
            "payload": {
                "google": {
                    "expectUserResponse": True,
                    "richResponse": {
                        "items": [
                            {
                                "simpleResponse": {
                                    "textToSpeech": question['text']
                                }
                            }
                        ]
                    }
                }
            },
            "outputContexts": outputContexts
        }
    )
