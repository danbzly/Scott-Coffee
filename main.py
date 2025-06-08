from flask import Flask, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

app = Flask(__name__)

# Setup Google Sheets API from JSON in environment variable
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
google_creds_json = os.environ.get("GOOGLE_CREDS_JSON")
if not google_creds_json:
    raise ValueError("Missing GOOGLE_CREDS_JSON environment variable")

creds_dict = json.loads(google_creds_json)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Update this with your actual spreadsheet and worksheet names
SHEET_NAME = "Scott Coffee Results"
WORKSHEET_NAME = "Scott Coffee Results"

try:
    spreadsheet = client.open(SHEET_NAME)
    worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
    print("Worksheet accessed successfully:", worksheet.title)
except gspread.exceptions.SpreadsheetNotFound:
    print("Error: Spreadsheet not found. Check SHEET_NAME.")
    raise
except gspread.exceptions.WorksheetNotFound:
    print("Error: Worksheet not found. Check WORKSHEET_NAME.")
    raise

@app.route('/')
def home():
    return jsonify({"message": "Welcome to Streamline Events API. Send a POST request to /get_participant with first_name and last_name."})

@app.route('/get_participant', methods=['POST'])
def get_participant():
    try:
        data = request.json
        if not data or "first_name" not in data or "last_name" not in data:
            return jsonify({"error": "Missing first_name or last_name in JSON payload."}), 400

        first_name = data.get("first_name", "").strip().lower()
        last_name = data.get("last_name", "").strip().lower()

        raw_data = worksheet.get_all_values()
        if not raw_data:
            return jsonify({"error": "Sheet is empty."}), 500

        headers = raw_data[0]
        records = raw_data[1:]

        # Normalize column names
        col_indices = {h: headers.index(h) for h in headers}

        for row in records:
            name = row[col_indices.get("Name", -1)].strip().lower() if "Name" in col_indices els]()
