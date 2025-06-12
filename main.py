import os
import base64
import mimetypes
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from file_processor import extract_text_from_file
from summary import summarize_text_gemini

# Define Gmail API OAuth scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    """Handles OAuth authentication and refresh token management."""
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())

    return creds

def get_gmail_service():
    """Returns an authenticated Gmail service object."""
    creds = authenticate_gmail()
    return build('gmail', 'v1', credentials=creds)

def get_emails_with_attachments(service):
    """Fetches emails containing attachments."""
    query = "has:attachment"
    results = service.users().messages().list(userId='me', q=query).execute()
    emails = results.get('messages', [])
    print(f"🔍 Found {len(emails)} emails with attachments.")
    return emails

def download_all_attachments(service, email_id):
    """Downloads all attachments from an email."""
    message = service.users().messages().get(userId='me', id=email_id).execute()
    parts = message.get('payload', {}).get('parts', [])

    os.makedirs("downloads", exist_ok=True)
    downloaded_files = []

    for part in parts:
        filename = part.get('filename')
        if filename:
            attachment_id = part['body'].get('attachmentId')
            if attachment_id:
                attachment = service.users().messages().attachments().get(
                    userId='me', messageId=email_id, id=attachment_id
                ).execute()

                file_data = base64.urlsafe_b64decode(attachment['data'])
                file_path = os.path.join("downloads", filename)

                with open(file_path, "wb") as f:
                    f.write(file_data)

                print(f"📥 Downloaded: {file_path}")
                downloaded_files.append(file_path)

    return downloaded_files

def save_summary(filename, summary):
    """Saves the summary to a text file."""
    os.makedirs("summaries", exist_ok=True)
    summary_path = os.path.join("summaries", filename + ".txt")

    with open(summary_path, "w") as f:
        f.write(summary)

    print(f"💾 Summary saved: {summary_path}")

# Authenticate Gmail API
creds = authenticate_gmail()
service = build('gmail', 'v1', credentials=creds)
print("✅ Gmail API authenticated successfully!")

# Fetch emails with attachments
emails = get_emails_with_attachments(service)

if emails:
    for email in emails:
        file_paths = download_all_attachments(service, email['id'])

        for file_path in file_paths:
            file_text = extract_text_from_file(file_path)  # Process any file type

            if file_text:
                summary = summarize_text_gemini(file_text, filename=os.path.basename(file_path))
                print(f"📝 Summary for {file_path}:\n{summary}")

                save_summary(os.path.basename(file_path), summary)
else:
    print("❌ No emails with attachments found.")