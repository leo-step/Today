from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from dotenv import load_dotenv
from mixpanel import Mixpanel
from clients import db_client
from datetime import datetime, timezone
from models import Event, ChatQueryInput
from tools import tools, choose_tool_and_rewrite, invoke_tool
from response import generate_response
from memory import Memory, ToolInvocation, MessageType
import os
import uuid

load_dotenv()

app = Flask(__name__, static_folder='dist', static_url_path='/')
mp = Mixpanel(os.getenv("MIXPANEL"))

CORS(app, resources={r"/*": {"origins": "*"}})

# ========== UI ==========

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('dist', filename)

@app.route('/')
def index():
    return send_from_directory('dist', 'index.html')

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
    app.run(debug=True)
