from services import SpreadsheetReader
from services import IntentsSyncronizer
import os
import json
from pprint import pprint

# name of the intent that starts the game
INTENT_PARENT = 'game'


def main():
    syncronize_intents()


def syncronize_intents():
    creds = os.environ.get('DIALOGFLOW_CREDS')
    intents = get_intents()
    intents_syncronizer = IntentsSyncronizer(creds, INTENT_PARENT)
    intents_syncronizer.syncronize_intents(intents)


def get_intents():
    key = os.environ.get('KEY')
    credentials_file = os.environ.get('SHEET_CREDENTIALS_FILE')

    reader = SpreadsheetReader(key, credentials_file)
    return reader.get_values_from_sheet()


if __name__ == "__main__":
    main()
