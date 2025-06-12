import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise Exception("Missing or invalid token.json")

    return creds

def get_gmail_service():
    creds = authenticate_gmail()
    return build("gmail", "v1", credentials=creds)

def download_attachments_by_message_id(service, message_id):
    import base64
    message = service.users().messages().get(userId='me', id=message_id, format='full').execute()
    payload = message.get('payload', {})
    parts = payload.get('parts', [])
    os.makedirs("downloads", exist_ok=True)
    files = []

    for part in parts:
        filename = part.get("filename")
        mime_type = part.get("mimeType")
        body = part.get("body", {})
        attachment_id = body.get("attachmentId")

        if filename and attachment_id:
            # Traditional attachment
            attachment = service.users().messages().attachments().get(
                userId='me', messageId=message_id, id=attachment_id
            ).execute()
            data = base64.urlsafe_b64decode(attachment['data'])
        elif filename and "data" in body:
            # Inline attachment (especially .txt)
            data = base64.urlsafe_b64decode(body['data'])
        else:
            continue  # skip empty or unsupported parts

        path = os.path.join("downloads", filename)
        with open(path, "wb") as f:
            f.write(data)
        files.append(path)

    return files
