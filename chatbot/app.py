import os
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load .env for local development
load_dotenv()

# Prompt
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        ("user", "Question: {question}")
    ]
)

# LLM (works locally + Streamlit Cloud)
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.5,
    api_key=os.getenv("GROQ_API_KEY")
)

# Chain
chain = prompt | llm | StrOutputParser()

# UI
st.title("🤖 Chatbot with Groq (LLaMA 3)")
question = st.text_input("Ask something")

if question:
    st.write(chain.invoke({"question": question}))
