import os

from flask import Flask, request

from main import syncronize_intents

app = Flask(__name__)


@app.route("/sync")
def sync():
    token = request.args.get('token')

    if not token or os.environ.get('TOKEN') != token:
        return 'Forbidden'

    syncronize_intents()
    return "Sincronización completada con éxito"
