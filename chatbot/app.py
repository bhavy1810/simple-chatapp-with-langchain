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


st.set_page_config(
    page_title="PromptlyAI",
    page_icon="🤖",
    layout="wide"
)

st.markdown(
    """
    <style>
    /* ---------------- Global ---------------- */
    html, body, [class*="css"] {
        font-family: 'Inter', 'SF Pro Display', 'Segoe UI', Arial, sans-serif;
        background-color: #020617;
        color: #e5e7eb;
    }

    /* ---------------- Answer Card ---------------- */
    .answer-box {
        background: linear-gradient(180deg, #0f172a, #020617);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 14px;
        padding: 22px 24px;
        line-height: 1.65;
        font-size: 15px;
        box-shadow:
            0 10px 30px rgba(2, 6, 23, 0.7),
            inset 0 1px 0 rgba(255, 255, 255, 0.04);
    }

    /* ---------------- Headings ---------------- */
    .answer-box h2 {
        font-size: 18px;
        font-weight: 600;
        margin-top: 18px;
        margin-bottom: 10px;
        color: #f8fafc;
        letter-spacing: -0.2px;
    }

    .answer-box h3 {
        font-size: 16px;
        font-weight: 600;
        margin-top: 16px;
        margin-bottom: 8px;
        color: #e2e8f0;
    }

    /* ---------------- Paragraphs ---------------- */
    .answer-box p {
        margin-bottom: 10px;
        color: #e5e7eb;
    }

    /* ---------------- Lists ---------------- */
    .answer-box ul {
        padding-left: 20px;
        margin-top: 8px;
        margin-bottom: 8px;
    }

    .answer-box li {
        margin-bottom: 6px;
        color: #d1d5db;
    }

    .answer-box li::marker {
        color: #38bdf8;
    }

    /* ---------------- Inline Code ---------------- */
    .answer-box code {
        background: rgba(148, 163, 184, 0.12);
        padding: 2px 6px;
        border-radius: 6px;
        font-size: 13px;
        color: #f1f5f9;
    }

    /* ---------------- Code Blocks ---------------- */
    div[data-testid="stCodeBlock"] pre {
        white-space: pre-wrap !important;
        word-break: break-word !important;
        overflow-x: hidden !important;
        background: #020617 !important;
        border-radius: 12px !important;
        border: 1px solid rgba(148, 163, 184, 0.15);
        padding: 16px !important;
        font-size: 14px !important;
        line-height: 1.6 !important;
    }

    /* ---------------- Subtle Accent ---------------- */
    .promptly-accent {
        color: #38bdf8;
        font-weight: 500;
    }
    </style>
    """,
    unsafe_allow_html=True
)


load_dotenv()

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are Promptly — a calm, precise, and professional AI assistant.

YOUR WRITING STYLE:
• Think before answering  
• Be confident, not verbose  
• Sound human, not robotic  

STRUCTURE RULES:
• Start with a short, clear explanation (1–2 lines max)
• Then use bullet points or steps when useful
• Use headings only when they add clarity
• Avoid unnecessary repetition

QUALITY STANDARDS:
• Be technically accurate
• No assumptions or hallucinations
• If unsure, clearly say so
• Prefer clarity over cleverness

FORMATTING PREFERENCES:
• Clean spacing
• Short paragraphs
• Bullets for lists
• Code only when relevant

GOAL:
Deliver answers that feel:
✓ Thoughtful  
✓ Easy to scan  
✓ Immediately useful  
"""
        ),
        ("user", "{question}")
    ]
)

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.5,
    api_key=os.getenv("GROQ_API_KEY")
)

chain = prompt | llm | StrOutputParser()

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

st.session_state.setdefault("question", "")
st.session_state.setdefault("response", "")
st.session_state.setdefault("last_generated_question", "")

st.title("🤖 Chat with PromptlyAI")

user_question = st.text_input(
    "Ask something",
    value=st.session_state.question
)

if user_question and user_question != st.session_state.last_generated_question:
    st.session_state.question = user_question
    st.session_state.response = chain.invoke({"question": user_question})
    st.session_state.last_generated_question = user_question

if st.session_state.response:
    st.subheader("Answer")

    st.markdown(
        f"<div class='answer-box'>{st.session_state.response}</div>",
        unsafe_allow_html=True
    )

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

        st.download_button(
            label="📄 Export as PDF",
            data=pdf,
            file_name="promptly_answer.pdf",
            mime="application/pdf"
        )
