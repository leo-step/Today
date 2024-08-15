from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from email.utils import parsedate_tz, mktime_tz
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import base64
import os

load_dotenv()

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def extract_text_and_links_from_html(html_string: str):
    soup = BeautifulSoup(html_string, 'html.parser')
    text = soup.get_text(strip=True)
    links = [a['href'] for a in soup.find_all('a', href=True)]
    return text, list(set(links))

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
    text_parts = []
    extracted_links = []
    msg = service.users().messages().get(userId='me', id=message_id, format='full').execute()
    
    payload = msg['payload']
    headers = payload['headers']
    
    subject = next(header['value'] for header in headers if header['name'] == 'Subject')
    sender = next(header['value'] for header in headers if header['name'] == 'From')
    date_header = next(header['value'] for header in headers if header['name'] == 'Date')
    
    # Convert the date to a Unix timestamp
    parsed_date = parsedate_tz(date_header)
    email_timestamp = int(mktime_tz(parsed_date))
    
    text_parts.append(f"Subject: {subject}")
    text_parts.append(f"From: {sender}")
    
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                body = part['body']
                data = body.get('data')
                if data:
                    html = base64.urlsafe_b64decode(data).decode()
                    text, links = extract_text_and_links_from_html(html)
                    text_parts.append(f"Body: {text}")
                    extracted_links = links
    else:
        body = payload['body']
        data = body.get('data')
        if data:
            html = base64.urlsafe_b64decode(data).decode()
            text, links = extract_text_and_links_from_html(html)
            text_parts.append(f"Body: {text}")
            extracted_links = links

    doc = Document(
        page_content="\n".join(text_parts), 
        metadata={"id": message_id, "links": extracted_links, "time": email_timestamp}
    )

    return doc

def main():
    is_dry_run = True
    service = get_gmail_service()
    
    # Replace with the specific email address you're looking for
    specific_email = "WHITMANWIRE@princeton.edu"
    
    # Search for unread emails sent to the specific email address
    query = f"to:{specific_email} is:unread"
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    
    if not messages:
        print("[INFO] No unread emails found.")
        return
    
    docs = []
    for message in messages:
        doc = read_email(service, message['id'])
        print(doc.page_content)
        print(doc.metadata)
        print("\n\n===================\n\n")
        docs.append(doc)

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    connection = "postgresql+psycopg://langchain:langchain@localhost:6024/langchain"
    collection_name = "emails"

    vector_store = PGVector(
        embeddings=embeddings,
        collection_name=collection_name,
        connection=connection,
        use_jsonb=True,
    )

    if not is_dry_run:
        vector_store.add_documents(docs, ids=[doc.metadata["id"] for doc in docs])

        print(f"[INFO] added {len(docs)} email documents")
        
        # Mark the email as read
        # service.users().messages().modify(
        #     userId='me', 
        #     id=message['id'], 
        #     body={'removeLabelIds': ['UNREAD']}
        # ).execute()
    else:
        print("[INFO] finished email dry run")

if __name__ == '__main__':
    main()