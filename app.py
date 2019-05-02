import os
import json

from flask import Flask, request, jsonify, g
from slugify import slugify

from services import QuestionService, PersistService, SpreadsheetReader
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
    print(request_dialogflow)
    session_id = request_dialogflow['session'].split('/')[-1]
    request_text = request_dialogflow['queryResult']['queryText']
    questions = persist_service.get_questions()
    question_service = QuestionService(PROJECT_ID, session_id, questions)

    # TODO Save questions already answered on session
    question = question_service.get_question()
    new_context = question_service.get_context('question')
    game_context = question_service.get_context('game')
    gamefollowup_context = question_service.get_context('game-followup')
    question_object = question_service.get_question_from_context(
        request_dialogflow['queryResult']['outputContexts'],
        new_context
    )

    if request_text in question_service.FINISH_GAME_SENTENCES:
        output_contexts = []
    else:
        if question_object:
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

            response = question_service.get_response_to_question(
                request_text, question_object)
        else:
            response = question['text']
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
                    "name": new_context,
                    "lifespanCount": 1,
                    "parameters": {
                        'question': question['context']
                    }
                }
            ]

    return jsonify(
        question_service.get_dialogflow_response(
            response, question, output_contexts)
    )
