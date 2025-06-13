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
    print("📩 message_id received:", message_id)

    if not message_id:
        print("❌ Missing message_id in request")
        return jsonify({"error": "Missing message_id"}), 400

    try:
        service = get_gmail_service()
        print("✅ Gmail service initialized")

        files = download_attachments_by_message_id(service, message_id)
        print("📎 Files downloaded:", files)

        summaries = []
        for file in files:
            print("🧾 Processing file:", file)
            content = extract_text_from_file(file)
            if content:
                summary = summarize_text_gemini(content, filename=os.path.basename(file))
                summaries.append({"file": os.path.basename(file), "summary": summary})

        print("✅ Summaries ready:", summaries)
        return jsonify({"summaries": summaries}), 200

    except Exception as e:
        print("🔥 Exception occurred:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))  # Render sets PORT env var automatically
    app.run(host="0.0.0.0", port=port)
