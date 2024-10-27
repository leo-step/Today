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
import json
import hashlib

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
    if os.getenv("GMAIL_TOKEN_JSON"):
        with open('token.json', 'w') as fp:
            fp.write(os.getenv("GMAIL_TOKEN_JSON"))
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        except json.JSONDecodeError:
            os.remove('token.json')
    
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

def compute_email_hash(subject, sender, body):
    email_content = f"{subject}{sender}{body}"
    return hashlib.md5(email_content.encode('utf-8')).hexdigest()

def read_email(service, message_id):
    text_parts = []
    extracted_links = []
    ids = []
    docs = []

    msg = service.users().messages().get(userId='me', id=message_id, format='full').execute()
    payload = msg['payload']
    headers = payload['headers']

    # extract headers case-sensitively
    subject = next(
        header['value'].strip()
        for header in headers
        if header['name'].lower() == 'subject'
    )
    sender = next(
        header['value'].strip()
        for header in headers
        if header['name'].lower() == 'from'
    )
    date_header = next(
        header['value'].strip()
        for header in headers
        if header['name'].lower() == 'date'
    )

    # Convert the date to a Unix timestamp
    parsed_date = parsedate_tz(date_header)
    email_timestamp = int(mktime_tz(parsed_date))

    # Emphasize the subject line
    text_parts.append(f"SUBJECT: {subject}")
    text_parts.append(f"From: {sender}")

    # Extract the email body and links
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                body = part['body']
                data = body.get('data')
                if data:
                    text = base64.urlsafe_b64decode(data).decode()
                    text_parts.append(f"Body: {text}")
            elif part['mimeType'] == 'text/html':
                body = part['body']
                data = body.get('data')
                if data:
                    html = base64.urlsafe_b64decode(data).decode()
                    text, links = extract_text_and_links_from_html(html)
                    text_parts.append(f"Body: {text}")
                    extracted_links.extend(links)
    else:
        body = payload['body']
        data = body.get('data')
        if data:
            html = base64.urlsafe_b64decode(data).decode()
            text, links = extract_text_and_links_from_html(html)
            text_parts.append(f"Body: {text}")
            extracted_links.extend(links)

    page_content = "\n".join(text_parts)

    # Compute 'expiry_time' using 'get_expiry_time'
    expiry_time = get_expiry_time(page_content, email_timestamp)

    # Determine if the email is from an eating club
    eating_club = is_eating_club(page_content)

    # Use message_id as the document ID
    doc_id = message_id

    # 'received_time' field to store when the email was processed
    # Will help prioritize recent emails
    received_time = int(time.time())

    # Include 'subject' in the metadata
    metadata = {
        "subject": subject,
        "links": extracted_links,
        "time": email_timestamp,
        "expiry": expiry_time,
        "source": "email",
        "received_time": received_time
    }

    docs.append(Document(
        page_content=page_content,
        metadata=metadata
    ))
    ids.append(doc_id)

    if eating_club:
        # Modify the 'source' for eating club emails
        metadata_ec = metadata.copy()
        metadata_ec["source"] = "eatingclub"
        docs.append(Document(
            page_content=page_content,
            metadata=metadata_ec
        ))
        ids.append(doc_id + "__ec")

    return {
        "ids": ids,
        "docs": docs,
        "subject": subject
    }

def is_duplicate(message_id, processed_ids):
    return message_id in processed_ids

def main():
    is_dry_run = False
    service = get_gmail_service()
    
    # list of emails/listservs to check
    email_addresses = [
        "WHITMANWIRE@princeton.edu",
        "westwire@princeton.edu",
        "allug@princeton.edu",
        "freefood@princeton.edu",
        "matheymail@princeton.edu",
        "public-lectures@princeton.edu",
        "CampusRecInfoList@princeton.edu",
        "pace-center@princeton.edu",
        "tigeralert@princeton.edu",
    ]
    
    # modified the query to include emails where the listserv is in 'to' or 'cc'
    email_query = " OR ".join([f"(to:{email} OR cc:{email})" for email in email_addresses])

    # include forwarded emails by subject
    forwarded_query = "subject:(Fwd OR Forwarded)"

    # fetch all unread emails matching the criteria
    query = f"({email_query} OR {forwarded_query}) is:unread"

    print(f"Full query: {query}")

    all_messages = []
    page_token = None

    while True:
        # Fetch messages with pagination support
        response = service.users().messages().list(
            userId='me', q=query, pageToken=page_token
        ).execute()
        messages = response.get('messages', [])
        all_messages.extend(messages)
        
        # Check for the nextPageToken to continue fetching if it exists
        page_token = response.get('nextPageToken')
        if not page_token:
            break

    print(f"Total messages fetched: {len(all_messages)}")

    if not all_messages:
        print("[INFO] No unread emails found.")
        return

    processed_messages = []
    processed_ids = set()
    processed_subjects = set()
    ids = []
    docs = []
    # initialize a set to collect all message IDs to mark as read
    message_ids_to_mark_as_read = set()

    for message in all_messages:
        message_id = message['id']
        message_ids_to_mark_as_read.add(message_id)

        # Get the email headers with case-insensitive key matching
        msg = service.users().messages().get(
            userId='me',
            id=message_id,
            format='metadata',
            metadataHeaders=['Subject']
        ).execute()
        headers = msg['payload']['headers']

        # normalize subject header (sometimes it's caps and sometimes not)
        # i genuinely have no idea why
        subject = next(
            header['value'].strip()
            for header in headers
            if header['name'].lower() == 'subject'
        ).lower() 

        # normalize subject line
        normalized_subject = ' '.join(subject.split())

        # skip if processed
        if normalized_subject in processed_subjects:
            print(f"[INFO] Skipping duplicate email with subject: {subject}")
            continue
        else:
            processed_subjects.add(normalized_subject)
            print(f"[INFO] Processing email with subject: {subject}")

        msg_data = read_email(service, message_id)
        if not msg_data:
            continue  # skip if email content couldnt be read

        processed_messages.append(msg_data)
        processed_ids.add(message_id)

        ids.extend(msg_data["ids"])
        docs.extend(msg_data["docs"])

    print(f"Total unique messages to add: {len(docs)}")

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
        try:
            if docs:
                # before adding documents, check for existing IDs
                existing_ids = set()
                existing_docs_cursor = atlas_collection.find({'_id': {'$in': ids}}, {'_id': 1})
                for doc in existing_docs_cursor:
                    existing_ids.add(doc['_id'])

                # filter out documents with existing ids
                new_docs = []
                new_ids = []
                for doc, id_ in zip(docs, ids):
                    if id_ not in existing_ids:
                        new_docs.append(doc)
                        new_ids.append(id_)
                    else:
                        print(f"[INFO] Skipping document with duplicate _id: {id_}")

                if new_docs:
                    vector_store.add_documents(new_docs, ids=new_ids)
                    print(f"[INFO] Added {len(new_docs)} new email documents:")
                    for doc in new_docs:
                        print(f" - {doc.metadata.get('subject', 'No Subject')}")
                else:
                    print("[INFO] All documents already exist in the collection.")
            else:
                print("[INFO] No new documents to add.")

            # mark all processed emails as read, including duplicates
            for msg_id in message_ids_to_mark_as_read:
                service.users().messages().modify(
                    userId='me',
                    id=msg_id,
                    body={'removeLabelIds': ['UNREAD']}
                ).execute()

            print(f"[INFO] Marked {len(message_ids_to_mark_as_read)} emails as read.")
        except Exception as e:
            print(f"[ERROR] Failed to process emails: {e}")
    else:
        print("[INFO] Finished email dry run")

if __name__ == '__main__':
    main()
