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
    dialogflow_credentials_file = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    with open(dialogflow_credentials_file) as f:
       project_id = json.load(f).get('project_id')

    intents = get_intents()
    intents_syncronizer = IntentsSyncronizer(project_id, INTENT_PARENT)
    intents_syncronizer.syncronize_intents(intents)

def get_intents():
    key = os.environ.get('KEY')
    credentials_file = os.environ.get('SHEET_CREDENTIALS_FILE')

    reader = SpreadsheetReader(key, credentials_file)
    return reader.get_values_from_sheet()

if __name__ == "__main__":
    main()

