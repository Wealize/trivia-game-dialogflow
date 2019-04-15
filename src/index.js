const fs = require("fs");
const readline = require("readline");
const { google } = require("googleapis");

const SPREADSHEET_ID = '1HkpC8xspETya5J6njJCNZQSXyGpUsYi71VNySChj3_E';
const RANGE_SPREADSHEET = 'Sheet1!A2:C';
const SCOPES = [
  "https://spreadsheets.google.com/feeds",
  "https://www.googleapis.com/auth/drive"
];
const TOKEN_PATH = "token.json";

fs.readFile("credentials.json", (err, content) => {
  if (err) return console.log("Error loading client secret file:", err);
  authorize(JSON.parse(content), listIntents);
});

function authorize(credentials, callback) {
    const {client_secret, client_id, redirect_uris} = credentials.installed;
    const oAuth2Client = new google.auth.OAuth2(
        client_id, client_secret, redirect_uris[0]);

    // Check if we have previously stored a token.
    fs.readFile(TOKEN_PATH, (err, token) => {
      if (err) return getNewToken(oAuth2Client, callback);
      oAuth2Client.setCredentials(JSON.parse(token));
      callback(oAuth2Client);
    });
  }

  function getNewToken(oAuth2Client, callback) {
    const authUrl = oAuth2Client.generateAuthUrl({
      access_type: 'offline',
      scope: SCOPES,
    });

    console.log('Authorize this app by visiting this url:', authUrl);

    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    });

    rl.question('Enter the code from that page here: ', (code) => {
      rl.close();
      oAuth2Client.getToken(code, (err, token) => {
        if (err) return console.error('Error while trying to retrieve access token', err);

        oAuth2Client.setCredentials(token);

        fs.writeFile(TOKEN_PATH, JSON.stringify(token), (err) => {
          if (err) return console.error(err);
          console.log('Token stored to', TOKEN_PATH);
        });

        callback(oAuth2Client);
      });
    });
  }

  function listIntents(auth) {
    const sheets = google.sheets({version: 'v4', auth});
    sheets.spreadsheets.values.get({
      spreadsheetId: SPREADSHEET_ID,
      range: RANGE_SPREADSHEET,
    }, (err, res) => {
      if (err) return console.log('The API returned an error: ' + err);

      const rows = res.data.values;

      if (rows.length) {
        console.log(`${rows.length} intents found.`)
        return rows;
      } else {
        console.log('No data found.');
      }
    });
  }
