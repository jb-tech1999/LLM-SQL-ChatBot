from openai import OpenAI
import os
from sqlalchemy import create_engine, Text
import pandas as pd
from chromadb.utils import embedding_functions
import chromadb


def setup(DSN: str, collection_name: str):
  OPENAI_API_KEY = ""

  #query database to get all views
  engine = create_engine(f"mssql+pyodbc://{DSN}")
  
  query = """
  SELECT
      *
  FROM
      INFORMATION_SCHEMA.VIEWS
  """
  views = pd.read_sql(query, engine)

  #loop through all views to get the TABLE_NAME, save the VIEW_DEFINITION to a file with the name of the TABLE_NAME.sql
  for index, row in views.iterrows():
      table_name = row["TABLE_NAME"]
      v_query = rf"SELECT OBJECT_DEFINITION(OBJECT_ID(N'dbo.{table_name}'))"
      view_def = pd.read_sql(v_query, engine)
      view_definition = view_def[""].values[0]
      with open(f"views/{table_name}.sql", "w") as f:
          f.write(view_definition)
          f.close()

  client = chromadb.PersistentClient(path='embeddings')
  #client = chromadb.Client()
  client.heartbeat()
  
  id = 1
  #loop through all files in the views directory and upload them to the chromadb
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
  
  print(collection.count())
