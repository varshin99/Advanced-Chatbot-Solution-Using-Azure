import os
import streamlit as st
from langchain.llms import OpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import Chroma
from langchain.agents.agent_toolkits import (
    create_vectorstore_agent,
    VectorStoreToolkit,
    VectorStoreInfo
)

# Initialize Streamlit app with finance-related title and icon
st.set_page_config(page_title="Finance GPT", page_icon="💲", layout="wide")

# Use custom styling for headers and content
st.markdown("""
    <style>
        .big-font {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            font-size: 200%;
            color: #264653;
        }
        .subtitle-font {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            color: #2a9d8f;
            font-size: 120%;
        }
        .report-content {
            font-family: serif;
            background-color: #e9f5db;
            padding: 2em;
            border-radius: 0.5em;
            margin-top: 1em;
        }
    </style>
""", unsafe_allow_html=True)

# Display a title and a subtitle in big font with markdown
st.markdown('<div class="big-font">💰 Finance GPT</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-font">Explore financial documents with the power of GPT.</div>', unsafe_allow_html=True)

# Sidebar for API key input
with st.sidebar:
    st.markdown("## Settings 🛠️")
    api_key = st.text_input("Enter your OpenAI API key", type="password")

# Check if API key is entered and set it in the environment
if api_key:
    os.environ['OPENAI_API_KEY'] = api_key

# If API key is present, proceed with app logic
if 'OPENAI_API_KEY' in os.environ:
    llm = OpenAI(temperature=0.1, verbose=True)
    embeddings = OpenAIEmbeddings()

    # Main content area with input and output in columns
    col1, col2 = st.columns([3, 2])
    
    with col1:
        prompt = st.text_input('Input your prompt here', placeholder="Ask a finance-related question...")
    
    with col2:
        st.markdown('<div class="report-content">Enter a prompt related to finance to get insights from your document collection.</div>', unsafe_allow_html=True)
    
    if prompt:
        # Process prompt using the LLM and vector store
        vectorstore_info = VectorStoreInfo(
            name="annual_report",
            description="a banking annual report as a PDF",
            vectorstore=st.session_state.vectorstore
        )
        toolkit = VectorStoreToolkit(vectorstore_info=vectorstore_info)
        agent_executor = create_vectorstore_agent(
            llm=llm,
            toolkit=toolkit,
            verbose=True
        )
        response = agent_executor.run(prompt)
        st.write(response)

        # Document Similarity Search Expander
        with st.expander('💼 Document Similarity Search'):
            try:
                search = st.session_state.vectorstore.similarity_search_with_score(prompt)
                if search:
                    st.markdown(f'<div class="report-content">{search[0][0].page_content}</div>', unsafe_allow_html=True)
                else:
                    st.write("No similar documents found.")
            except Exception as e:
                st.error(f"An error occurred during the similarity search: {e}")
else:
    st.error("Please enter your OpenAI API key in the sidebar.")

# Initialize the Chroma vector store if not already done
if 'OPENAI_API_KEY' in os.environ and 'vectorstore' not in st.session_state:
    with st.spinner('Loading document collection...'):
        loader = PyPDFLoader('annualreport.pdf')
        pages = loader.load_and_split()
        st.session_state.vectorstore = Chroma.from_documents(pages, embeddings, collection_name='annualreport')
