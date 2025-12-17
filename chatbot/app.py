import os
from urllib import response
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        ("user", "Question: {question}")
    ]
)

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.5,
    api_key=os.getenv("GROQ_API_KEY")
)

chain = prompt | llm | StrOutputParser()

st.title("🤖 Chat with Promptly ")
question = st.text_input("Ask something")

if question:
    response = chain.invoke({"question": question})
    st.subheader("Answer")
    st.code(response, language="markdown")