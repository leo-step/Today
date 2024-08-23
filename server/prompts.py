from utils import system_prompt, user_prompt
from memory import Memory

@user_prompt
def user_query(text: str):
    return text

@system_prompt
def tool_and_rewrite(memory: Memory, query_text: str):
    return "Return a JSON in the format {\"tool\": \"tool_name\"} where tool_name is either \"Crawl\" \"Emails\" or null"

@system_prompt
def respond_with_context(context: str):
    return f"Answer the user's question using the following documents as context:\n\n{context}"