from email.header import decode_header
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)

def read_email(service, message_id):
    msg = service.users().messages().get(userId='me', id=message_id, format='full').execute()
    
    payload = msg['payload']
    headers = payload['headers']
    
    subject = next(header['value'] for header in headers if header['name'] == 'Subject')
    sender = next(header['value'] for header in headers if header['name'] == 'From')
    
    print(f"Subject: {subject}")
    print(f"From: {sender}")
    
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                body = part['body']
                data = body.get('data')
                if data:
                    text = base64.urlsafe_b64decode(data).decode()
                    print(f"Body: {text}")
    else:
        body = payload['body']
        data = body.get('data')
        if data:
            text = base64.urlsafe_b64decode(data).decode()
            print(f"Body: {text}")
    
    print("\n" + "="*50 + "\n")

def main():
    service = get_gmail_service()
    
    # Replace with the specific email address you're looking for
    specific_email = "leo.stepanewk@gmail.com"
    
    # Search for unread emails sent to the specific email address
    query = f"from:{specific_email} is:unread"
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    
    if not messages:
        print("No unread emails found.")
        return
    
    for message in messages:
        read_email(service, message['id'])
        
        # Mark the email as read
        service.users().messages().modify(
            userId='me', 
            id=message['id'], 
            body={'removeLabelIds': ['UNREAD']}
        ).execute()

if __name__ == '__main__':
    main()