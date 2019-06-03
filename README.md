# Dialogflow trivia game webhook

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/baa2ad5839174faead849433e0ed0e15)](https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=TheNeonProject/trivia-game-dialogflow&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/baa2ad5839174faead849433e0ed0e15)](https://www.codacy.com?utm_source=github.com&utm_medium=referral&utm_content=TheNeonProject/trivia-game-dialogflow&utm_campaign=Badge_Coverage)
[![Gitlab CI Badge](https://gitlab.com/TheNeonProject/trivia-game-dialogflow/badges/master/pipeline.svg)](https://gitlab.com/TheNeonProject/trivia-game-dialogflow)

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
