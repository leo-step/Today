from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from email.utils import parsedate_tz, mktime_tz
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from langchain_mongodb import MongoDBAtlasVectorSearch
from pymongo import MongoClient
import base64
import os
from preprocess import get_expiry_time, is_eating_club
import time

load_dotenv()

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def extract_text_and_links_from_html(html_string: str):
    soup = BeautifulSoup(html_string, 'html.parser')
    text = soup.get_text(strip=True)
    links = [a['href'] for a in soup.find_all('a', href=True)]
    return text, list(set(links))

def get_gmail_service():
    token_json = os.getenv("GMAIL_TOKEN_JSON")
    with open("token.json", "w") as fp:
        fp.write(token_json)
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

    page_content = "\n".join(text_parts)

    expiry_time = get_expiry_time(page_content, int(time.time()))
    eating_club = is_eating_club(page_content)

    ids = []
    docs = []

    docs.append(Document(
        page_content=page_content, 
        metadata={"links": extracted_links, "time": email_timestamp, 
                  "expiry": expiry_time, "source": "email"}
    ))
    ids.append(message_id)
    if eating_club:
        docs.append(Document(
            page_content=page_content, 
            metadata={"links": extracted_links, "time": email_timestamp, 
                    "expiry": expiry_time, "source": "eatingclub"}
        ))
        ids.append(message_id + "__ec")

    return ids, docs

def main():
    is_dry_run = False
    service = get_gmail_service()
    
    # Replace with the specific email address you're looking for
    specific_email = "WHITMANWIRE@princeton.edu"
    
    # Search for unread emails sent to the specific email address
    query = f"to:{specific_email} is:unread"
    all_messages = []
    page_token = None

    while True:
        # Fetch messages with pagination support
        response = service.users().messages().list(userId='me', q=query, pageToken=page_token).execute()
        messages = response.get('messages', [])
        all_messages.extend(messages)
        
        # Check for the nextPageToken to continue fetching if it exists
        page_token = response.get('nextPageToken')
        if not page_token:
            break

    if not all_messages:
        print("[INFO] No unread emails found.")
        return

    ids = []
    docs = []
    for message in all_messages:
        msg_ids, msg_docs = read_email(service, message['id'])
        ids.extend(msg_ids)
        docs.extend(msg_docs)

    embeddings = OpenAIEmbeddings(model="text-embedding-3-large", dimensions=256)

    client = MongoClient(os.getenv("MONGO_CONN"))
    # Define collection and index name
    db_name = "today"
    collection_name = "crawl"
    atlas_collection = client[db_name][collection_name]

    vector_store = MongoDBAtlasVectorSearch(
        atlas_collection,
        embeddings
    )

    if not is_dry_run:
        # atlas_collection.delete_many(
        #     { "source": "email" },
        # )

        vector_store.add_documents(docs, ids=ids)

        # Mark the email as read
        for msg_id in ids:
            service.users().messages().modify(
                userId='me', 
                id=msg_id, 
                body={'removeLabelIds': ['UNREAD']}
            ).execute()

        print(f"[INFO] added {len(docs)} email documents")
    else:
        print("[INFO] finished email dry run")

if __name__ == '__main__':
    main()