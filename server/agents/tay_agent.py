import os

from chains.crawl_hybrid_search_chain import crawl_hybrid_search_chain
from langchain import hub
from langchain.tools import StructuredTool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from models.tool_inputs import SingleTextInput

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
    )
]

chat_model = ChatOpenAI(
    model=AGENT_MODEL,
    temperature=0,
)

tay_agent = create_openai_functions_agent(
    llm=chat_model,
    prompt=agent_prompt,
    tools=tools,
)

tay_agent_executor = AgentExecutor(
    agent=tay_agent,
    tools=tools,
    return_intermediate_steps=True,
    verbose=True,
)
