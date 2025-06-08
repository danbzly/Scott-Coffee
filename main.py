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
            name = row[col_indices.get("Name", -1)].strip().lower() if "Name" in col_indices else ""
            if not name:
                continue
            parts = name.split()
            if len(parts) < 2:
                continue
            row_first_name = parts[0].strip().lower()
            row_last_name = parts[-1].strip().lower()

            if row_first_name == first_name and row_last_name == last_name:
                response = {
                    "result": {
                        "Overall Place": row[col_indices.get("Overall Place", "")],
                        "Name": row[col_indices.get("Name", "")],
                        "Clock Time": row[col_indices.get("Clock Time", "")],
                        "Pace": row[col_indices.get("Pace", "")],
                        "Gender": row[col_indices.get("Gender", "")],
                        "Age": row[col_indices.get("Age", "")],
                        "Bib": row[col_indices.get("Bib", "")],
                        "PLP%": row[col_indices.get("PLP%", "")],
                        "City/Town": row[col_indices.get("City/Town", "")],
                        "State": row[col_indices.get("State", "")],
                        "Chip Time": row[col_indices.get("Chip Time", "")],
                        "Chip Pace": row[col_indices.get("Chip Pace", "")],
                        "Country": row[col_indices.get("Country", "")],
                        "Age Percentage": row[col_indices.get("Age Percentage", "")],
                        "Division Place": row[col_indices.get("Division Place", "")],
                        "Division": row[col_indices.get("Division", "")]
                    }
                }
                return jsonify(response)

        return jsonify({"error": "Participant not found."}), 404

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/debug_headers', methods=['GET'])
def debug_headers():
    try:
        headers = worksheet.row_values(1)
        return jsonify({"headers": headers})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 3000)))
