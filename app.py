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
    try:
        data = request.get_json(force=True)
        print("📩 Raw request data:", data)

        if not data or "message_id" not in data:
            print("❌ Missing or invalid message_id in request.")
            return jsonify({"error": "Missing or invalid message_id"}), 400

        message_id = data["message_id"]
        print("📩 message_id received:", message_id)

        service = get_gmail_service()
        print("✅ Gmail API service initialized")

        files = download_attachments_by_message_id(service, message_id)
        print(f"📎 Files downloaded: {files}")

        if not files:
            print("⚠️ No attachments found for this message.")
            return jsonify({"summaries": []}), 200

        summaries = []
        for file in files:
            print("🧾 Processing:", file)
            content = extract_text_from_file(file)

            if content:
                summary = summarize_text_gemini(content, filename=os.path.basename(file))
                summaries.append({
                    "file": os.path.basename(file),
                    "summary": summary
                })
            else:
                print(f"⚠️ No readable content extracted from {file}")

        print("✅ Summaries prepared:", summaries)
        return jsonify({"summaries": summaries}), 200

    except Exception as e:
        print("🔥 Exception during summarization:", str(e))
        return jsonify({"error": f"Server error: {str(e)}"}), 500



if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))  # Render sets PORT env var automatically
    app.run(host="0.0.0.0", port=port)
