import os
import json
from pprint import pprint

from services import SpreadsheetReader, IntentsSyncronizer

# name of the intent that starts the game
INTENT_PARENT = 'game'


def main():
    syncronize_intents()


def syncronize_intents():
    creds = json.loads(os.environ.get('DIALOGFLOW_CREDS'))
    intents = get_intents()
    intents_syncronizer = IntentsSyncronizer(creds, INTENT_PARENT)
    intents_syncronizer.syncronize_intents(intents)


def get_intents():
    key = os.environ.get('KEY')
    credentials = json.loads(os.environ.get('SHEETS_CREDS'))

    reader = SpreadsheetReader(key, credentials)
    return reader.get_values_from_sheet()


if __name__ == "__main__":
    main()
