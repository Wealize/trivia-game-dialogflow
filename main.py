import os
import json
import logging

from services import SpreadsheetReader, IntentsSyncronizer

# name of the intent that starts the game
INTENT_PARENT = 'game'


def main():
    syncronize_intents()


def syncronize_intents():
    intents = get_intents()
    print('Intents loaded: {}'.format(len(intents)))
    intents_syncronizer = IntentsSyncronizer(
        json.loads(os.environ.get('DIALOGFLOW_CREDS')),
        INTENT_PARENT
    )
    intents_syncronizer.syncronize_intents(intents)


def get_intents():
    spreadsheet_id = os.environ.get('SPREADSHEET_ID')
    credentials = json.loads(os.environ.get('SPREADSHEET_CREDENTIALS'))

    reader = SpreadsheetReader(spreadsheet_id, credentials)
    return reader.get_values_from_sheet()


if __name__ == "__main__":
    main()
