import os

from chains.crawl_hybrid_search_chain import crawl_hybrid_search_chain
from chains.email_hybrid_search_chain import email_hybrid_search_chain
from langchain import hub
from langchain.tools import StructuredTool
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from models.tool_inputs import SingleTextInput
from langchain.agents import AgentType, initialize_agent
from agents.utils import AsyncCallbackHandler
from agents.memory import MongoDBConversationMemory
from dotenv import load_dotenv
import os

load_dotenv()

AGENT_MODEL = os.getenv("AGENT_MODEL")

agent_prompt = hub.pull("hwchase17/openai-functions-agent")

tools = [
    StructuredTool(
        name="Crawl",
        func=crawl_hybrid_search_chain.invoke,
        description="""This tool accesses a crawl of all Princeton
        and Princeton-related webpages. Useful when you need to answer
        questions about the university, academic requirements, professors,
        various academic programs, general information about campus life,
        and other general things that would be listed on a university 
        webpage. 
        
        Not useful for answering questions that involve real time
        information about campus life, clubs, events, job opportunity 
        postings, and other similar kinds of information.

        Should be used as a default fallback when other tools don't 
        give a good response.
        
        Use the entire prompt as input to the tool. For instance, if 
        the prompt is "Who is Professor Arvind Narayanan?", the input 
        should be "Who is Professor Arvind Narayanan?".
        """,
        args_schema=SingleTextInput
    ),
    StructuredTool(
        name="Emails",
        func=email_hybrid_search_chain.invoke,
        description="""This tool accesses the latest Princeton listserv
        emails. Useful when you need to answer question about real time
        events, clubs, job opportunity postings, deadlines for auditions,
        and things going on in campus life.
        
        Not useful for answering questions about academic facts or 
        professors.
        
        Use the entire prompt as input to the tool. For instance, if 
        the prompt is "What dance shows are coming up?", the input 
        should be "What dance shows are coming up?".
        """,
        args_schema=SingleTextInput
    )
]

def get_agent_run_call(session_id):
    chat_model = ChatOpenAI(
        model=AGENT_MODEL,
        temperature=0,
        streaming=True
    )

    message_history = MongoDBConversationMemory(
        session_id=session_id,
        connection_string=os.getenv("MONGO_CONN"),
        database_name="today",
        collection_name="conversations",
        session_id_key="session_id",
        history_key="message"
    )

    memory = ConversationBufferMemory(
        chat_memory=message_history,
        memory_key='chat_history',
        return_messages=True,
    )

    tay_agent = initialize_agent(
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        tools=tools,
        llm=chat_model,
        verbose=True,
        max_iterations=3,
        early_stopping_method="generate",
        memory=memory,
        return_intermediate_steps=False
    )

    async def run_call(query: str, stream_it: AsyncCallbackHandler):
        tay_agent.agent.llm_chain.llm.callbacks = [stream_it]
        await tay_agent.acall(inputs={"input": query})

    return run_call
