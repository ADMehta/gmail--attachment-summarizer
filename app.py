from flask import Flask, request, jsonify
from main import get_gmail_service, download_attachments_by_message_id
from summary import summarize_text_gemini
from file_processor import extract_text_from_file
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Gmail Summarizer is live!"

@app.route("/summarize", methods=["POST"])
def summarize_handler():
    data = request.get_json()
    message_id = data.get("message_id")
    print("📩 Received message ID:", message_id)

    if not message_id:
        return jsonify({"error": "Missing message_id"}), 400

    try:
        service = get_gmail_service()
        files = download_attachments_by_message_id(service, message_id)
        print("📎 Attachments found:", files)


        summaries = []
        for file in files:
            content = extract_text_from_file(file)
            if content:
                summary = summarize_text_gemini(content, filename=os.path.basename(file))
                summaries.append({ "file": os.path.basename(file), "summary": summary })

        return jsonify({ "summaries": summaries }), 200

    except Exception as e:
        return jsonify({ "error": str(e) }), 500

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))  # Render sets PORT env var automatically
    app.run(host="0.0.0.0", port=port)
