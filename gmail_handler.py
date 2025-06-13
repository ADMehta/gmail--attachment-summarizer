import os
import base64
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_gmail_service():
    """Authenticate and return the Gmail API service."""
    print("🔐 Initializing Gmail service...")
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("♻️ Refreshing expired token...")
            creds.refresh(Request())
        else:
            raise Exception("❌ Missing or invalid token.json — make sure OAuth flow was completed.")

    print("✅ Gmail service ready.")
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
                # Traditional attachment
                attachment = service.users().messages().attachments().get(
                    userId="me", messageId=message_id, id=attachment_id
                ).execute()
                data = attachment.get("data")
            elif filename and "data" in body:
                # Inline base64-encoded body (e.g., .txt)
                data = body["data"]
            else:
                print(f"⚠️ Skipping part — no filename or data.")
                continue

            if data:
                file_data = base64.urlsafe_b64decode(data.encode("UTF-8"))
                path = os.path.join(save_dir, filename)
                with open(path, "wb") as f:
                    f.write(file_data)
                files.append(path)
                print(f"📎 Saved attachment: {path}")
        except Exception as e:
            print(f"🔥 Failed to save {filename}: {e}")

    print(f"📦 Total attachments saved: {len(files)}")
    return files
