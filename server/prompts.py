from utils import system_prompt, user_prompt
from memory import Memory
from models import Tools

@user_prompt
def user_query(text: str):
    return text

@system_prompt
def respond_with_context(context: str):
    return f"Answer the user's question using the following documents as context:\n\n{context}"

@system_prompt
def tool_and_rewrite(tools: Tools, memory: Memory):
    messages = memory.get_messages()
    conversation_context = "\n\n".join(messages)

    tool_names = ", ".join([tool['name'].value for tool in tools])
    tool_descriptions = [f"Tool Name: {tool['name'].value}\nTool Description:{tool['description']}" for tool in tools]
    tool_context = "\n\n".join(tool_descriptions)
    
    prompt = f"""Here is the ongoing conversation between you and the user:
    {conversation_context}

    Here are the tools available to you to answer the user query:
    {tool_context}

    You need to return a JSON with the following two keys:

    "tool": TOOL_NAME where TOOL_NAME is one of {tool_names}.

    "query_rewrite": CONTEXTUALIZED_QUERY where CONTEXTUALIZED_QUERY is a rewritten version of the user query,
    which is imbued with context from the ongoing conversation. An example is if the user asks "Tell me more
    about him" and the ongoing conversation is about Professor Arvind Narayanan, CONTEXTUALIZED_QUERY should be
    something like "Tell me more about Professor Arvind Narayanan." The contextualized rewrite of the query
    should include whatever information you think is necessary to make it an effective, standalone query.
    """

    return prompt
