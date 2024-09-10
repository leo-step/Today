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
import json
from openai import OpenAI
from datetime import datetime, timedelta
import pytz

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
        metadata={"links": extracted_links, "time": email_timestamp, "source": "email"}
    )

    return message_id, doc

openai_client = OpenAI()

def openai_json_response(messages, model="gpt-4o-mini", temp=1, max_tokens=1024):
    response = openai_client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temp,
        max_tokens=max_tokens,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={
            "type": "json_object"
        }
    )
    return json.loads(response.choices[0].message.content)

def get_expiry_time(doc):
    result = openai_json_response([{
        "role": "system",
        "content": [
            {
                "type": "text",
                "text": f"""{doc.page_content}\n\nReturn a JSON with key 'time' and value in the format MM-DD-YYYY 
                where the date is the latest date found in this email. Consider all the dates! It's important to find
                the latest date out of all of them, no matter the format. Today's date is Tuesday, September 10th, 
                2024, and you can use this fact to reason about any relative dates. If there is no date referenced,
                return null for the time."""
            }
        ]
    }])

    date_str = result['time']
    if date_str:
        ny_tz = pytz.timezone('America/New_York')
        date_obj = datetime.strptime(date_str, '%m-%d-%Y')
        ny_midnight = ny_tz.localize(date_obj)
        return int(ny_midnight.timestamp())
    else:
        current_time = datetime.now()
        one_week_from_now = current_time + timedelta(weeks=1)
        return int(one_week_from_now.timestamp())


def main():
    is_dry_run = False
    service = get_gmail_service()
    
    # Replace with the specific email address you're looking for
    specific_email = "WHITMANWIRE@princeton.edu"
    
    # Search for unread emails sent to the specific email address
    query = f"to:{specific_email}"
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

    _, doc = read_email(service, all_messages[2]['id'])

    print(get_expiry_time(doc))

    

    
if __name__ == '__main__':
    main()