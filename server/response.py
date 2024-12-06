from memory import Memory, MessageType, ToolInvocation
from prompts import user_query_with_context, agent_system_prompt
from utils import openai_stream

def generate_response(memory: Memory, tool_use: ToolInvocation):
    query = tool_use["input"]
    context = tool_use["output"]
    full_response = []

    try:
        response = openai_stream([
            agent_system_prompt(),
            user_query_with_context(context, query)
        ])
        
        for chunk in response:
            chunk_content = chunk.choices[0].delta.content
            if chunk_content != None:
                full_response.append(chunk_content)
                yield chunk_content
    except Exception as e:
        print(e)

    content = ''.join(full_response)
    memory.add_message(MessageType.AI, content, tool_use=tool_use)
