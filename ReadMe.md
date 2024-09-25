# ChromaDB Integration for View Uploads and Streamlit Chat

This README provides a comprehensive guide to using ChromaDB for uploading view definitions from a directory, querying them, and building a simple chat application using Streamlit. The code leverages OpenAI's embedding functions for efficient storage and retrieval of data.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
- [Code Explanation](#code-explanation)
- [Usage](#usage)
- [License](#license)

## Prerequisites

Before running the code, ensure you have the following:

1. **Python** installed on your machine (version 3.7 or higher).
2. **ChromaDB**, **OpenAI**, and **Streamlit** Python packages. Install them using:
   ```bash
   pip install chromadb openai streamlit
   ```
3. An **OpenAI API Key**. You can obtain one by signing up on the [OpenAI website](https://www.openai.com/).

## Setup Instructions

1. **Clone this repository** (if applicable):
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Prepare the Views Directory**: 
   Create a directory named `views` in the same directory as your script and place your view definition files (e.g., `.sql` files) in it.

3. **Configure Your API Key and Collection Name**:
   - Update the `OPENAI_API_KEY` variable in the code with your OpenAI API key.
   - Specify your collection name in the `get_or_create_collection` method call.

## Code Explanation

### Importing Libraries

```python
from chromadb.utils import embedding_functions
import chromadb
import os
import streamlit as st
from openai import OpenAI
```

This imports necessary modules from ChromaDB, Streamlit, and OpenAI, enabling interaction with the database, web app interface, and embedding functions.

### Client Initialization

```python
client = chromadb.PersistentClient(path='embeddings')
client.heartbeat()
```

This creates a persistent client for ChromaDB that will store embeddings in a directory named `embeddings`.

### OpenAI Embedding Function Setup

```python
OPENAI_API_KEY = ""  # Add your OpenAI API key here
openai_ef = embedding_functions.OpenAIEmbeddingFunction(api_key=OPENAI_API_KEY, model_name='text-embedding-ada-002')
```

This initializes the OpenAI embedding function using the specified model.

### Collection Creation

```python
collection = client.get_or_create_collection(name='', embedding_function=openai_ef)
```

Creates or retrieves a collection where the embedded view definitions will be stored.

### Uploading View Definitions

The following block reads all files in the `views` directory, processes the content, and uploads it to the ChromaDB collection.

```python
print("Uploading views to ChromaDB")
id = 1
for file in os.listdir("views"):
    with open(f"views/{file}", "r") as f:
        view_definition = f.read().replace("\n", " ").replace("\t", " ")
        
    collection.add(
        documents=[f"{view_definition}"],
        metadatas=[{"Source": f"{file}"}],
        ids=[f"{id}"]
    )
    id += 1

print("Upload complete")
print(collection.count())
```

### Streamlit Chat Application

The following code snippet sets up a simple chat interface using Streamlit:

```python
chat_client = OpenAI(api_key=OPENAI_API_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("How can I help?"):
    # Display your message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Query ChromaDB based on your prompt
    q = collection.query(query_texts=[prompt], n_results=3)
    results = q["documents"][0]

    prompts = []
    for r in results:
        prompt = "Please extract the following: " + prompt + \
            " solely based on the text below. Use your expert SQL skills to help answer questions. If you're unsure of the answer, say you cannot find the answer. \n\n" + r
        prompts.append(prompt)
    prompts.reverse()

    openai_res = chat_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "assistant", "content": prompt} for prompt in prompts],
        temperature=0,
    )

    response = openai_res.choices[0].message.content
    
    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
```

### Querying the Collection

You can query the collection using the following code, which is integrated into the Streamlit application to provide relevant responses based on user input.

## Usage

1. Place your view definition files in the `views` directory.
2. Set your OpenAI API key and collection name in the script.
3. Run the Streamlit application:
   ```bash
   streamlit run your_script.py
   ```
4. Use the chat interface to interact with the application, asking questions related to your PDF documents.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

Feel free to modify any sections to better fit your specific requirements!
