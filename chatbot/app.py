import os
import streamlit as st
from dotenv import load_dotenv
from io import BytesIO
import streamlit.components.v1 as components
import base64

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(
    page_title="PromptlyAI",
    page_icon="🤖",
    layout="wide"
)

# --------------------------------------------------
# Global Styles
# --------------------------------------------------
st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-family: Arial, Helvetica, sans-serif;
    }

    .answer-box {
        background-color: #0f172a;
        color: #e5e7eb;
        padding: 18px;
        border-radius: 12px;
        line-height: 1.6;
        font-size: 15px;
    }

    .answer-box ul {
        padding-left: 20px;
        margin-top: 8px;
    }

    .answer-box li {
        margin-bottom: 6px;
    }

    .answer-box h3 {
        margin-top: 14px;
        font-size: 17px;
        font-weight: 600;
    }

    div[data-testid="stCodeBlock"] pre {
        white-space: pre-wrap !important;
        word-break: break-word !important;
        overflow-x: hidden !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# Environment
# --------------------------------------------------
load_dotenv()

# --------------------------------------------------
# Prompt Template
# --------------------------------------------------
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are Promptly — a precise, thoughtful, and professional AI assistant.

STYLE & PRESENTATION:
- Prefer bullet points
- Clean spacing
- Clear structure

ROLE:
- Accurate, concise, and readable answers
- No hallucinations

FORMAT:
- Bullet points by default
- Headings when useful
"""
        ),
        ("user", "{question}")
    ]
)

# --------------------------------------------------
# LLM
# --------------------------------------------------
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.5,
    api_key=os.getenv("GROQ_API_KEY")
)

# --------------------------------------------------
# Chain
# --------------------------------------------------
chain = prompt | llm | StrOutputParser()

# --------------------------------------------------
# PDF Generator
# --------------------------------------------------
def generate_pdf(question: str, answer: str) -> BytesIO:
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>PromptlyAI Answer</b>", styles["Title"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>Question</b>", styles["Heading2"]))
    story.append(Paragraph(question, styles["BodyText"]))
    story.append(Spacer(1, 14))

    story.append(Paragraph("<b>Answer</b>", styles["Heading2"]))

    for line in answer.split("\n"):
        story.append(Paragraph(line, styles["BodyText"]))
        story.append(Spacer(1, 6))

    doc.build(story)
    buffer.seek(0)
    return buffer


# --------------------------------------------------
# Session State
# --------------------------------------------------
st.session_state.setdefault("question", "")
st.session_state.setdefault("response", "")
st.session_state.setdefault("last_generated_question", "")

# --------------------------------------------------
# UI
# --------------------------------------------------
st.title("🤖 Chat with PromptlyAI")

# -------------------- Input -----------------------
user_question = st.text_input(
    "Ask something",
    value=st.session_state.question
)

# ✅ Generate ONLY if question changed
if user_question and user_question != st.session_state.last_generated_question:
    st.session_state.question = user_question
    st.session_state.response = chain.invoke({"question": user_question})
    st.session_state.last_generated_question = user_question

# -------------------- Response --------------------
if st.session_state.response:
    st.subheader("Answer")

    st.markdown(
        f"<div class='answer-box'>{st.session_state.response}</div>",
        unsafe_allow_html=True
    )

    # ✅ COPY BUTTON
    encoded = base64.b64encode(
        st.session_state.response.encode("utf-8")
    ).decode("utf-8")

    components.html(
        f"""
        <button style="
            background:#020617;
            border:1px solid #334155;
            color:#e5e7eb;
            padding:6px 12px;
            border-radius:6px;
            cursor:pointer;
            margin-top:5px;
        "
        onclick="
            const text = atob('{encoded}');
            const ta = document.createElement('textarea');
            ta.value = text;
            document.body.appendChild(ta);
            ta.select();
            ta.setSelectionRange(0, 999999);
            document.execCommand('copy');
            document.body.removeChild(ta);

            const t=document.getElementById('toast');
            t.style.opacity=1;
            setTimeout(()=>t.style.opacity=0,2000);
        ">
            📋 Copy
        </button>

        <div id="toast" style="
            position:fixed;
            bottom:20px;
            right:20px;
            background:#020617;
            color:#e5e7eb;
            padding:8px 12px;
            border-radius:6px;
            opacity:0;
            transition:.3s;
        ">
            Copied!
        </div>
        """,
        height=70
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 Regenerate Answer"):
            st.session_state.response = chain.invoke(
                {"question": st.session_state.question}
            )

    with col2:
        pdf = generate_pdf(
            st.session_state.question,
            st.session_state.response
        )

        # ✅ DOES NOT REGENERATE
        st.download_button(
            label="📄 Export as PDF",
            data=pdf,
            file_name="promptly_answer.pdf",
            mime="application/pdf"
        )
