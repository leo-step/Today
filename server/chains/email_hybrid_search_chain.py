import os

from langchain.chains import RetrievalQA
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from retrievers.hybrid_search import MongoHybridRetriever
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

embeddings = OpenAIEmbeddings(model="text-embedding-3-large", dimensions=256)

client = MongoClient(os.getenv("MONGO_CONN"))
db_name = "today"
collection_name = "emails"
atlas_collection = client[db_name][collection_name]

QA_MODEL = os.getenv("AGENT_MODEL")

crawl_template = """Your job is to use Princeton email data
data to answer student questions. Use the following context to 
answer questions.

Be as detailed as possible, but don't make up any information
that's not from the context. If you don't know an answer,
say you don't know. When writing out the text of your response,
include all the relevant links from the emails used. Pay very
specific attention to the "How recent" aspect of each email.
Prioritize using the most recent information and notify the 
user if the information available is potentially stale by
saying what time period you had to look back for your response.

{context}
"""

system_prompt = SystemMessagePromptTemplate(
    prompt=PromptTemplate(
        input_variables=["context"], template=crawl_template
    )
)

human_prompt = HumanMessagePromptTemplate(
    prompt=PromptTemplate(input_variables=["question"], template="{question}")
)
messages = [system_prompt, human_prompt]

email_response_prompt = ChatPromptTemplate(
    input_variables=["context", "question"], messages=messages
)

hybrid_retriever = MongoHybridRetriever(
    collection=atlas_collection,
    embeddings=embeddings,
)

email_hybrid_search_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model=QA_MODEL, temperature=0),
    chain_type="stuff",
    retriever=hybrid_retriever,
    # return_source_documents=True
)

email_hybrid_search_chain.combine_documents_chain.llm_chain.prompt = email_response_prompt

# print(crawl_hybrid_search_chain.invoke("Arvind Narayanan"))