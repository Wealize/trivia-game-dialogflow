import os

from flask import Flask, request, jsonify

from main import syncronize_intents

app = Flask(__name__)


@app.route("/sync")
def sync():
    token = request.args.get('token')

    if not token or os.environ.get('TOKEN') != token:
        return 'Forbidden'

    syncronize_intents()
    return "Sincronización completada con éxito"


@app.route("/hook", methods=['POST'])
def webhook():
    token = request.args.get('token')

    if not token or os.environ.get('TOKEN') != token:
        return 'Forbidden'

    request_dialogflow = request.get_json()
    session_id = request_dialogflow['session'].split('/')[-1]
    print(request_dialogflow)
    print(session_id)
    return jsonify(
        {
            "fulfillmentText": "Holiiii",
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": ["Mi respuestica"]
                    }
                }
            ],
            "source": "vocento.com",
            "payload": {
                "google": {
                    "expectUserResponse": True,
                    "richResponse": {
                        "items": [
                            {
                                "simpleResponse": {
                                    "textToSpeech": "Esto es una respuesta simple"
                                }
                            }
                        ]
                    }
                }
            },
            "outputContexts": [
                {
                    "name": "projects/vocento-staging/agent/sessions/{}/contexts/pliki".format(session_id),
                    "lifespanCount": 5,
                    "parameters": {}
                }
            ]
        }
    )
