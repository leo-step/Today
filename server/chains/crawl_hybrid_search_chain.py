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
collection_name = "crawl"
atlas_collection = client[db_name][collection_name]

QA_MODEL = os.getenv("AGENT_MODEL")

crawl_template = """Your job is to use Princeton website
data to answer student questions. Use the following context to 
answer questions.

Be as detailed as possible, but don't make up any information
that's not from the context. If you don't know an answer,
say you don't know. After writing out the text of your
response, include all the relevant links you used as well.

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

crawl_response_prompt = ChatPromptTemplate(
    input_variables=["context", "question"], messages=messages
)

hybrid_retriever = MongoHybridRetriever(
    collection=atlas_collection,
    embeddings=embeddings,
)

crawl_hybrid_search_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model=QA_MODEL, temperature=0),
    chain_type="stuff",
    retriever=hybrid_retriever,
    # return_source_documents=True
)

crawl_hybrid_search_chain.combine_documents_chain.llm_chain.prompt = crawl_response_prompt

# print(crawl_hybrid_search_chain.invoke("Arvind Narayanan"))