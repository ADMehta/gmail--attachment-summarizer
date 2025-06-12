import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Scopes required to read Gmail metadata and attachments
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    """Loads credentials from token.json. Must be pre-generated locally."""
    creds = None

    # Check token.json exists
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise Exception("Missing or invalid token.json. Run locally to authorize.")

    return creds

def get_gmail_service():
    creds = authenticate_gmail()
    return build('gmail', 'v1', credentials=creds)

def get_emails_with_attachments(service):
    """Returns a list of messages with attachments."""
    response = service.users().messages().list(userId='me', q="has:attachment").execute()
    return response.get('messages', [])

def download_all_attachments(service, email_id):
    """Downloads all attachments from a message and returns local file paths."""
    import base64
    message = service.users().messages().get(userId='me', id=email_id).execute()
    parts = message.get('payload', {}).get('parts', [])
    os.makedirs("downloads", exist_ok=True)
    files = []

    for part in parts:
        filename = part.get("filename")
        attachment_id = part.get("body", {}).get("attachmentId")
        if filename and attachment_id:
            attachment = service.users().messages().attachments().get(
                userId='me', messageId=email_id, id=attachment_id
            ).execute()
            data = base64.urlsafe_b64decode(attachment['data'])
            file_path = os.path.join("downloads", filename)
            with open(file_path, "wb") as f:
                f.write(data)
            files.append(file_path)

    return files
