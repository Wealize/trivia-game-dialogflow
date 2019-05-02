# Vocento-game sincronización

## Run

En local, exportar antes las variables de entorno:
```bash
export GOOGLE_APPLICATION_CREDENTIALS='CREDS_FILE' KEY='KEY_SHEET' SHEET_CREDENTIALS_FILE='SPREADHEET_CREDENTIALS_FILE'
```

Para ejecutar el scrip:
```bash
pipenv run python3 main.py
```

## Tests

Para ejecutar los tests:
```bash
pipenv run python3 -m pytest tests/ --cov=. --disable-warnings
```
