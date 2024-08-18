import os

from chains.crawl_hybrid_search_chain import crawl_hybrid_search_chain
from langchain import hub
from langchain.agents import AgentExecutor, Tool, create_openai_functions_agent
from langchain_openai import ChatOpenAI

AGENT_MODEL = os.getenv("AGENT_MODEL")

agent_prompt = hub.pull("hwchase17/openai-functions-agent")

tools = [
    Tool(
        name="Experiences",
        func=crawl_hybrid_search_chain.invoke,
        description="""Useful when you need to answer questions
        about patient experiences, feelings, or any other qualitative
        question that could be answered about a patient using semantic
        search. Not useful for answering objective questions that involve
        counting, percentages, aggregations, or listing facts. Use the
        entire prompt as input to the tool. For instance, if the prompt is
        "Are patients satisfied with their care?", the input should be
        "Are patients satisfied with their care?".
        """,
    ),
]

chat_model = ChatOpenAI(
    model=AGENT_MODEL,
    temperature=0,
)

hospital_rag_agent = create_openai_functions_agent(
    llm=chat_model,
    prompt=agent_prompt,
    tools=tools,
)

tay_agent_executor = AgentExecutor(
    agent=hospital_rag_agent,
    tools=tools,
    return_intermediate_steps=True,
    verbose=True,
)
