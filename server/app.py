from flask import Flask, request, jsonify, send_from_directory, \
    session, redirect, url_for, abort, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from mixpanel import Mixpanel
from clients import db_client
from datetime import datetime, timezone
from models import Event, ChatQueryInput
from tools import tools, choose_tool_and_rewrite, invoke_tool
from response import generate_response
from memory import Memory, ToolInvocation, MessageType
from cas import CASClient
from urllib.parse import urlparse, parse_qs
import os
import uuid

load_dotenv()

app = Flask(__name__, static_folder='dist', static_url_path='/')
app.secret_key = os.getenv("APP_SECRET_KEY")

mp = Mixpanel(os.getenv("MIXPANEL"))

CORS(app, resources={r"/*": {"origins": "*"}})

cas_client = CASClient()

def authenticated(request):
    if request.args.get('uuid'):
        return True
    
    referer = request.headers.get('Referer')
    if referer:
        parsed_url = urlparse(referer)
        query_params = parse_qs(parsed_url.query)
        
        if 'uuid' in query_params:
            return True
    
    return cas_client.is_logged_in()

# ========== UI ==========

@app.route('/static/<path:filename>')
def serve_static(filename):
    # if not authenticated(request):
    #     abort(401)
    return send_from_directory('dist', filename)

@app.route('/')
def index():
    if not authenticated(request):
        return redirect(url_for("login"))
    return send_from_directory('dist', 'index.html')

@app.route("/login")
def login():
    cas_client.authenticate()
    next = url_for("index")
    if "next" in session:
        next = session.pop("next")
    return redirect(next)

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

# ========== EXTENSION ==========

@app.route('/api/extension/widget-data', methods=['GET'])
def widget_data():
    data = db_client['widgets'].find_one({'_id': 'data'})
    if data:
        data["timestamp"] = str(datetime.now(timezone.utc))
    return jsonify(data)

@app.route('/api/track', methods=['POST'])
def track():
    data = request.get_json()
    data = Event(**data)
    mp.track(data.uuid, data.event, data.properties)
    return '', 204

# ========== CHATBOT ==========

@app.route('/api/chat', methods=['POST'])
def chat():
    if not authenticated(request):
        abort(401)
    data = request.get_json()
    query = ChatQueryInput(**data)
    memory = Memory(query.uuid, query.session_id)

    tool, query_rewrite = choose_tool_and_rewrite(tools, memory, query.text)
    tool_result = invoke_tool(tool, query_rewrite)
    tool_use = ToolInvocation(
        tool=tool,
        input=query_rewrite,
        output=tool_result
    )

    memory.add_message(MessageType.HUMAN, query.text)
    mp.track(query.uuid, "chat", {'session_id': query.session_id})

    return generate_response(memory, tool_use), {"Content-Type": "text/plain"}

# ========== iOS SHORTCUT ==========

@app.route("/api/ios_chat", methods=['GET'])
def ios_chat():
    query = request.args.get('query')

    temp_uuid = "ios_chat"
    temp_session_id = str(uuid.uuid4())

    memory = Memory(temp_uuid, temp_session_id)

    tool, query_rewrite = choose_tool_and_rewrite(tools, memory, query)
    tool_result = invoke_tool(tool, query_rewrite)
    tool_use = ToolInvocation(
        tool=tool,
        input=query_rewrite,
        output=tool_result
    )

    memory.add_message(MessageType.HUMAN, query)
    mp.track(temp_uuid, "chat", {'session_id': temp_session_id})

    # use list to collect the repsonse chunks
    response_chunks = []
    for chunk in generate_response(memory, tool_use):
        response_chunks.append(chunk)
    
    # join all chunks into single response
    full_response = ''.join(response_chunks)
    
    return jsonify({"response": full_response})

if __name__ == '__main__':
    app.run(host="localhost", port=6001, debug=True)
