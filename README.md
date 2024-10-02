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

Run `app.py` to start the server, then call the endpoints through [Postman](https://www.postman.com/):
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
#### Development
If you want to use local server, switch URL in `src/config.tsx` to the DEV url.
```
cd extension
npm install
npm start
```
#### Release
Before creating a production build:
1. Return the url in `src/config.tsx` back to the PROD url.
2. Bump the version number in `public/manifest.json` and commit.
```
npm run build
```
Then zip the build folder and upload to the Chrome extension store.

### Chatbot
#### Development
If you want to use local server, switch URL in `src/config.tsx` to the DEV url.
```
cd chatbot
npm install
npm run dev
```
#### Release
Before creating a production build:
1. Return the url in `src/config.tsx` back to the PROD url.
```
npm run build
cd ..
git add .
git commit -m "build"
```
The last steps are required because the build command updates the `dist` folder in `server`.

## Deployment (ask Leo)

### Chatbot UI and server (for widget data and chatbot)
```
git subtree push --prefix server heroku main
```

### Core extension
Follow the release steps and zip the build folder and upload to the Chrome extension store. Remember to accurately update the description and screenshots if new visual features were added.
