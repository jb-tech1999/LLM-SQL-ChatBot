import streamlit as st
from chromadb.utils import embedding_functions
import chromadb
from openai import OpenAI

client = chromadb.PersistentClient(path='embeddings')
client.heartbeat()



OPENAI_API_KEY = "" #add own OpenAIKey
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=OPENAI_API_KEY, model_name='text-embedding-ada-002')
collection = client.get_or_create_collection(
    name='', embedding_function=openai_ef)                #Remeber to add own collection name

chat_client = client = OpenAI(api_key=OPENAI_API_KEY)


if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What do you want to say to your PDF?"):
    # Display your message
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add your message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # query ChromaDB based on your prompt, taking the top 5 most relevant result. These results are ordered by similarity.
    q = collection.query(
        query_texts=[prompt],
        n_results=3,
    )
    results = q["documents"][
        0
    ]

    prompts = []
    for r in results:
        # construct prompts based on the retrieved text chunks in results
        prompt = "Please extract the following: " + prompt + \
            "  solely based on the text below. Use your expert SQL Skills to help answer questions. If you're unsure of the answer, say you cannot find the answer. \n\n" + r

        prompts.append(prompt)
    prompts.reverse()

    openai_res = chat_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "assistant", "content": prompt}
                  for prompt in prompts],
        temperature=0,
    )

    response = openai_res.choices[0].message.content
    
    with st.chat_message("assistant"):
        st.markdown(response)

    # append the response to chat history
    st.session_state.messages.append(
        {"role": "assistant", "content": response})
