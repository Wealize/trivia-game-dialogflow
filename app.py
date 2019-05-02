import os
import json

from flask import Flask, request, jsonify, g
from slugify import slugify

from services import QuestionStateService, PersistService, SpreadsheetReader
from middleware import check_authentication


INTENT_PARENT = 'game'
PROJECT_ID = os.environ.get('PROJECT_ID')
SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')
CREDENTIALS = json.loads(os.environ.get('SPREADSHEET_CREDENTIALS'))
app = Flask(__name__)
persist_service = PersistService(os.environ.get('REDIS_URL'))


@app.route("/sync")
@check_authentication
def sync():
    reader = SpreadsheetReader(SPREADSHEET_ID, CREDENTIALS)
    questions = reader.get_values_from_sheet()
    persist_service.set_questions(questions)

    return "Sincronización completada con éxito"


@app.route("/hook", methods=['POST'])
@check_authentication
def webhook():
    request_dialogflow = request.get_json()

    try:
        session_id = request_dialogflow['session'].split('/')[-1]
        request_text = request_dialogflow['queryResult']['queryText']
        request_contexts = request_dialogflow['queryResult']['outputContexts']
    except (KeyError, IndexError):
        return 'Not a valid Dialogflow webhook payload', 400

    questions = persist_service.get_questions()
    question_state = QuestionStateService(
        os.environ.get('PROJECT_ID'),
        session_id,
        request_contexts,
        questions,
        request_text
    )

    return jsonify(question_state.get_next_response())
