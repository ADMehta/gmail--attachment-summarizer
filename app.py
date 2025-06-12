from flask import Flask, render_template, request, jsonify
from main import get_gmail_service, get_emails_with_attachments, download_all_attachments
from file_processor import extract_text_from_file
from summary import summarize_text_gemini
import os

app = Flask(__name__)

def fetch_email_metadata():
    service = get_gmail_service()
    emails = get_emails_with_attachments(service)
    enriched = []

    for email in emails:
        msg = service.users().messages().get(userId='me', id=email['id'], format='metadata').execute()
        headers = msg.get("payload", {}).get("headers", [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
        from_ = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')

        enriched.append({
            "id": email['id'],
            "subject": subject,
            "from": from_,
            "date": date
        })
    return enriched

@app.route("/")
def index():
    emails = fetch_email_metadata()
    return render_template("index.html", emails=emails)

@app.route("/summarize", methods=["POST"])
def summarize_selected():
    ids = request.json.get("emailIds", [])
    service = get_gmail_service()
    summaries = []

    for eid in ids:
        files = download_all_attachments(service, eid)
        for f in files:
            text = extract_text_from_file(f)
            if text.strip():
                summary = summarize_text_gemini(text, os.path.basename(f))
                summaries.append({
                    "filename": os.path.basename(f),
                    "summary": summary
                })
    return jsonify(summaries)

if __name__ == "__main__":
    import threading
    import platform
    import subprocess

    def open_browser():
        url = "http://127.0.0.1:5000"
        system = platform.system()

        try:
            if system == "Darwin":
                subprocess.Popen(["open", "-a", "Google Chrome", url])
            elif system == "Windows":
                subprocess.Popen(["start", "chrome", url], shell=True)
            elif system == "Linux":
                subprocess.Popen(["google-chrome", url])
            else:
                print("🌐 Could not detect OS — opening in default browser.")
        except Exception as e:
            print(f"⚠️ Could not open Chrome: {e}")
    
    threading.Timer(1.5, open_browser).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

    # print("🚀 Launching Gmail Summarizer at http://127.0.0.1:5000")
    # app.run(debug=True, port=5000, host="127.0.0.1")
