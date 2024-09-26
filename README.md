# Today

## Folder Structure
```
.github/workflows - contains yaml files defining cron jobs

analysis - scripts to analyze and dump chatbot conversation data

chatbot - contains the React project for the chat interface

docs - html files that are deployed to github pages e.g. privacy policy

extension - has the React project for the Today chrome extension

pipelines - Python scripts to crawl websites and read emails, very messy

server - code for the widget data server and chatbot
```

## Installation

.env files will be provided to you.

### Server
```
cd server
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

To run the server, use
```
uvicorn main:app --reload
```
then call the endpoints through [Postman](https://www.postman.com/), for instance
```
POST http://127.0.0.1:8000/api/chat

(raw json)
{
    "text": "econ classes?",
    "uuid": "60da31a19-63e6-4ba7-ab80-c7eb4452be1a",
    "session_id": "asdf29"
}
```


### Extension
```
cd extension
npm install
npm start
```

### Chatbot
```
cd chatbot
npm install
npm run dev
```
