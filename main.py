from flask import Flask, request, jsonify
from file_processor import extract_text_from_file
from summary import summarize_text_gemini
from main import get_gmail_service, get_emails_with_attachments, download_all_attachments
import os

app = Flask(__name__)

@app.route("/")
def index():
    return "📬 Gmail Summarizer is up and running!"

@app.route("/summarize", methods=["POST"])
def summarize_handler():
    service = get_gmail_service()
    emails = get_emails_with_attachments(service)

    summaries = []
    for email in emails:
        file_paths = download_all_attachments(service, email['id'])
        for path in file_paths:
            text = extract_text_from_file(path)
            if text:
                summary = summarize_text_gemini(text, filename=os.path.basename(path))
                summaries.append({
                    "file": os.path.basename(path),
                    "summary": summary
                })

    return jsonify({"summaries": summaries})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
