import os
import json

from services import SpreadsheetReader, IntentsSyncronizer

# name of the intent that starts the game
INTENT_PARENT = 'game'


def main():
    syncronize_intents()


def syncronize_intents():
    creds = os.environ.get('DIALOGFLOW_CREDS')
    f = open(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'), 'a')
    f.write(creds)
    f.close()

    intents = get_intents()

    print('Intents: {}'.format(len(intents)))

    intents_syncronizer = IntentsSyncronizer(
        os.environ.get('PROJECT_ID'), INTENT_PARENT)
    intents_syncronizer.syncronize_intents(intents)


def get_intents():
    key = os.environ.get('KEY')
    credentials = json.loads(os.environ.get('SHEETS_CREDS'))

    reader = SpreadsheetReader(key, credentials)
    return reader.get_values_from_sheet()


if __name__ == "__main__":
    main()
