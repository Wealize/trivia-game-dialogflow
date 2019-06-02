# Dialogflow trivia game webhook

## Run

Executing the server locally

```bash
export GOOGLE_APPLICATION_CREDENTIALS='CREDS_FILE' KEY='KEY_SHEET' SHEET_CREDENTIALS_FILE='SPREADHEET_CREDENTIALS_FILE'

pipenv run python3 main.py
```

## Tests

```bash
pipenv run python3 -m pytest tests/ --cov=. --disable-warnings
```
