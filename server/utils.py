from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

def get_embedding(query_text, model="text-embedding-3-large", dimensions=256):
   query_text = query_text.replace("\n", " ")
   return client.embeddings.create(input = [query_text], model=model, dimensions=dimensions).data[0].embedding
