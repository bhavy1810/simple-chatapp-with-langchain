from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        ("user", "Question: {question}")
    ]
)

llm = ChatGroq(
    model="llama-3.1-8b-instant", 
    temperature=0.5
)

chain = prompt | llm | StrOutputParser()

st.title("🤖 Chatbot with Groq (LLaMA 3)")
question = st.text_input("Ask something")

if question:
    st.write(chain.invoke({"question": question}))
