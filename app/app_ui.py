###### SET UP ######

from qdrant_client import QdrantClient
from llama_index.core import VectorStoreIndex
from llama_index.core import StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.gemini import Gemini
from llama_index.core import PromptTemplate

import os
import streamlit as st
from dotenv import load_dotenv

from prompts import *
from utils import *

# load api key
load_dotenv()



# set up database, and avoiding re-initializing objects
if "client" not in st.session_state:
    # Initialize objects only if not present in session state
    st.session_state.client = QdrantClient(host="localhost", port=6333)
    st.session_state.embed_model = HuggingFaceEmbedding(model_name="KhoaUIT/Halong-UIT-R2GQA", max_length=512)
    st.session_state.qdrant_vector_store = QdrantVectorStore(
        client=st.session_state.client,
        collection_name="corpus_halong-trained",
        enable_hybrid=True
    )
    st.session_state.storage_context = StorageContext.from_defaults(vector_store=st.session_state.qdrant_vector_store)
    st.session_state.index = VectorStoreIndex.from_vector_store(
        vector_store=st.session_state.qdrant_vector_store,
        storage_context=st.session_state.storage_context,
        embed_model=st.session_state.embed_model
    )
    st.session_state.gemini_llm = Gemini(api_key=os.getenv("GEMINI_API_KEY"), model='models/gemini-2.0-flash-exp', temperature=0.0)

# Initialize session state for chat history. This will be used to store all chat messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Streamlit app title
st.title("Trợ lý Tuyển sinh UIT")


        
###### START CHAT ######

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if user_query := st.chat_input("Bạn có câu hỏi nào không?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(user_query)
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_query})

    # Retrieve relevant documents based on the query
    retriever = st.session_state.index.as_retriever(similarity_top_k=10, vector_store_query_mode="hybrid", alpha=0.5)
    nodes = retriever.retrieve(user_query)
    context_str = prepare_context_str(nodes)
    
    final_response = None
    filtered_response = filter_query(template_filter, user_query, st.session_state.gemini_llm)
    filtered_response = str(filtered_response).replace('\n', '')
    
    
    if filtered_response == "in-domain":
        response = answer_query(template_answer, user_query, context_str, st.session_state.gemini_llm)
        response = str(response).replace('\n', '')
        
        if response == "no information":
            final_response = TEMPLATE_RESPONSE_NO_INFORMATION
        else:
            final_response = response
            
    elif filtered_response == "out-of-domain":
        final_response = TEMPLATE_RESPONSE_OUT_OF_DOMAIN
            
    elif filtered_response == "prompt abuse":
        final_response = TEMPLATE_RESPONSE_ABUSE

    elif filtered_response == "not vietnamese":
        final_response = TEMPLATE_RESPONSE_NOT_VIETNAMESE

    else:
        # for greeting messages only
        final_response = filtered_response


    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(final_response)
        
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": final_response})