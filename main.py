from flask import Flask, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

app = Flask(__name__)

# Setup Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
google_creds_json = os.environ.get("GOOGLE_CREDS_JSON")

if not google_creds_json:
    raise ValueError("Missing GOOGLE_CREDS_JSON environment variable.")

creds_dict = json.loads(google_creds_json)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Replace with your actual sheet name
SHEET_NAME = "Your 2025 Bib Number"
WORKSHEET_NAME = "Your 2025 Bib Number"  # Change if needed

try:
    spreadsheet = client.open(SHEET_NAME)
    worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
    print("Worksheet accessed successfully:", worksheet.title)
    headers = worksheet.row_values(1)
except Exception as e:
    print("Error accessing Google Sheet:", str(e))
    worksheet = None

@app.route('/')
def home():
    return jsonify({"message": "Welcome to Streamline Events API. Send a POST request to /get_participant with first_name and last_name."})

@app.route('/get_participant', methods=['POST'])
def get_participant():
    if not worksheet:
        return jsonify({"error": "Worksheet not available."}), 500

    try:
        data = request.json
        if not data or "first_name" not in data or "last_name" not in data:
            return jsonify({"error": "Missing first_name or last_name in JSON payload."}), 400

        first_name = data["first_name"].strip().lower()
        last_name = data["last_name"].strip().lower()

        records = worksheet.get_all_records()

        for row in records:
            if row.get("Name", "").strip().lower() == f"{first_name} {last_name}":
                response = {
                    "result": {key: row.get(key, "") for key in [
                        "Overall Place", "Name", "Clock Time", "Pace", "Gender", "Age", "Bib",
                        "PLP%", "City/Town", "State", "Chip Time", "Chip Pace", "Country",
                        "Age Percentage", "Division Place", "Division"
                    ]}
                }
                return jsonify(response)

        return jsonify({"error": "Participant not found."}), 404

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/debug_headers', methods=['GET'])
def debug_headers():
    if not worksheet:
        return jsonify({"error": "Worksheet not available."}), 500

    try:
        return jsonify({
            "headers": worksheet.row_values(1),
            "sample_row": worksheet.get_all_records()[0] if worksheet.get_all_records() else {}
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 3000)))

