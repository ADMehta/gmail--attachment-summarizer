import os
import json
import base64
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_gmail_service():
    """Authenticate and return the Gmail API service."""
    print("🔐 Initializing Gmail service...")

    # ✅ Step 3: Validate token.json structure before loading
    try:
        with open("token.json") as f:
            creds_data = json.load(f)
            print("🗝 token.json keys:", creds_data.keys())

        missing = []
        for field in ["client_id", "client_secret", "refresh_token"]:
            if field not in creds_data or not creds_data[field]:
                missing.append(field)

        if missing:
            raise ValueError(f"❌ token.json is missing: {', '.join(missing)}")

    except Exception as e:
        print("🚨 Failed to load or validate token.json:", e)
        raise

    # Load credentials now that format is validated
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("♻️ Refreshing expired token...")
            creds.refresh(Request())
        else:
            raise Exception("❌ Invalid or expired Gmail credentials.")

    print("✅ Gmail service authorized.")
    return build("gmail", "v1", credentials=creds)

def download_attachments_by_message_id(service, message_id, save_dir="downloads"):
    """Downloads all attachments from a Gmail message."""
    print(f"📨 Fetching Gmail message: {message_id}")
    message = service.users().messages().get(userId="me", id=message_id, format="full").execute()
    payload = message.get("payload", {})
    parts = payload.get("parts", [])

    os.makedirs(save_dir, exist_ok=True)
    files = []

    for idx, part in enumerate(parts):
        filename = part.get("filename")
        mime_type = part.get("mimeType")
        body = part.get("body", {})
        attachment_id = body.get("attachmentId")

        print(f"🔍 Part {idx + 1}: {mime_type} — {filename}")

        try:
            if filename and attachment_id:
                attachment = service.users().messages().attachments().get(
                    userId="me", messageId=message_id, id=attachment_id
                ).execute()
                data = attachment.get("data")
            elif filename and "data" in body:
                data = body["data"]
            else:
                print("⚠️ Skipping part: no file or data found.")
                continue

            file_data = base64.urlsafe_b64decode(data.encode("UTF-8"))
            path = os.path.join(save_dir, filename)

            with open(path, "wb") as f:
                f.write(file_data)
            files.append(path)
            print(f"📎 Saved attachment: {path}")

        except Exception as e:
            print(f"🔥 Failed to process part: {e}")

    print(f"📦 Total attachments downloaded: {len(files)}")
    return files
