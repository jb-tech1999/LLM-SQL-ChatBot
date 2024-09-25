from chromadb.utils import embedding_functions
import chromadb
import os

client = chromadb.PersistentClient(path='embeddings')
client.heartbeat()

OPENAI_API_KEY = ""  #add own OpenAI API_KEY
openai_ef = embedding_functions.OpenAIEmbeddingFunction(api_key=OPENAI_API_KEY, model_name='text-embedding-ada-002')
collection = client.get_or_create_collection(name='BME_WestAfrica_views_embedded', embedding_function=openai_ef)

def setup_embeddings(collection_name: str):
  id = 1
  #loop through all files in the views directory and upload them to the chromadb
  print("Uploading views to ChromaDB")
  for file in os.listdir("views"):
      with open(f"views/{file}", "r") as f:
          view_definition = f.read()
          view_definition = view_definition.replace("\n", " ")
          view_definition = view_definition.replace("\t", " ")
  
      #print(file)
  
      openai_ef = embedding_functions.OpenAIEmbeddingFunction(api_key=OPENAI_API_KEY, model_name='text-embedding-ada-002')
      collection = client.get_or_create_collection(name=collection_name, embedding_function=openai_ef)
  
  
      collection.add(
          documents=[
              f"{view_definition}"
          ],
          metadatas=[
              {
                  "Source":f"{file}"
              }
          ],
          ids=[f"{id}"]
      )
      id += 1
  
  print("Upload complete")
  
  print(collection.count())

