import streamlit as st
from groq import Groq
from pypdf import PdfReader
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from xml.sax.saxutils import escape
import os

st.set_page_config(page_title="Study Buddy AI", page_icon="🎓", layout="wide")

MODEL = "openai/gpt-oss-20b"

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "quiz_history" not in st.session_state:
    st.session_state.quiz_history = []
if "notes_history" not in st.session_state:
    st.session_state.notes_history = []
if "generated_quizzes" not in st.session_state:
    st.session_state.generated_quizzes = 0
if "notes_created" not in st.session_state:
    st.session_state.notes_created = 0
if "last_quiz" not in st.session_state:
    st.session_state.last_quiz = ""
if "last_notes" not in st.session_state:
    st.session_state.last_notes = ""
if "last_activity" not in st.session_state:
    st.session_state.last_activity = "Ready to study"
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
if "quiz_topic" not in st.session_state:
    st.session_state.quiz_topic = ""

st.markdown("""
<style>
.stApp{background:#f5f8f6;color:#172b25}
[data-testid="stSidebar"]{background:#e8f1ec}
h1,h2,h3{color:#183f32}
div.stButton>button{border-radius:10px;border:1px solid #cbded3;font-weight:600}
div.stButton>button[kind="primary"]{background:#226b50;color:white;border:0}
div[data-testid="stMetric"]{background:white;padding:16px;border-radius:14px;border:1px solid #e1ebe5}
div[data-testid="stChatMessage"]{background:white;border-radius:12px}
.stDownloadButton>button{border-radius:9px}
.study-card{background:white;padding:18px;border-radius:14px;border:1px solid #e1ebe5;margin-bottom:10px}
.hero{background:linear-gradient(120deg,#174b38,#2b8060);color:white;padding:28px;border-radius:18px;margin-bottom:18px}
.hero h1{color:white;margin-bottom:8px}
.small-note{color:#62776c;font-size:14px}
</style>
""", unsafe_allow_html=True)

def get_client():
    key = st.secrets.get("GROQ_API_KEY", "")
    if not key:
        st.error("GROQ_API_KEY nahi mili. Streamlit Secrets mein API key add karo.")
        return None
    return Groq(api_key=key)

def ask_ai(prompt, max_tokens=4000, temperature=0.4):
    client = get_client()
    if client is None:
        return ""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature
    )
    return response.choices[0].message.content or ""

def extract_pdf_text(file):
    reader = PdfReader(file)
    text = []
    for page in reader.pages:
        text.append(page.extract_text() or "")
    return "\n".join(text).strip()

def make_pdf(text):
    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=A4, rightMargin=45, leftMargin=45, topMargin=45, bottomMargin=45)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleGreen", parent=styles["Title"], textColor=colors.HexColor("#226b50"), alignment=1, spaceAfter=18)
    heading_style = ParagraphStyle("HeadingGreen", parent=styles["Heading2"], textColor=colors.HexColor("#226b50"), spaceBefore=10, spaceAfter=6)
    body_style = ParagraphStyle("BodyText2", parent=styles["BodyText"], leading=15, spaceAfter=6)
    story = [Paragraph("STUDY BUDDY AI", title_style), Spacer(1, 8)]
    for line in text.splitlines():
        line = line.strip()
        if not line:
            story.append(Spacer(1, 5))
        elif line.startswith("#"):
            story.append(Paragraph(escape(line.lstrip("# ").strip()), heading_style))
        elif line.startswith(("- ", "* ", "• ")):
            story.append(Paragraph("• " + escape(line[2:].strip()), body_style))
        else:
            story.append(Paragraph(escape(line), body_style))
    doc.build(story)
    output.seek(0)
    return output.getvalue()

def show_heading(title, subtitle):
    st.title(title)
    st.caption(subtitle)

def go_to(page):
    st.session_state.page = page

with st.sidebar:
    st.markdown("## 🎓 Study Buddy AI")
    st.caption("Learn one concept at a time")
    pages = ["Dashboard", "AI Quiz", "PDF Notes", "Study Chat", "Performance", "Settings"]
    selected = st.radio("MENU", pages, index=pages.index(st.session_state.page))
    st.session_state.page = selected
    st.divider()
    st.caption("Powered by Groq AI")

if st.session_state.page == "Dashboard":
    st.markdown("""
    <div class="hero">
        <h1>Make every study session count.</h1>
        <p>Create quizzes, understand notes and learn one concept at a time.</p>
    </div>
    """, unsafe_allow_html=True)

    image_path = "assets/study_hero.png"
    if os.path.exists(image_path):
        st.image(image_path, use_container_width=True)

    a, b, c = st.columns(3)
    a.metric("Quizzes Created", st.session_state.generated_quizzes)
    b.metric("Notes Created", st.session_state.notes_created)
    c.metric("Chat Messages", len(st.session_state.chat_messages))
    st.subheader("What would you like to do?")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="study-card"><h3>📝 AI Quiz</h3><p>Practise topics with questions at your level.</p></div>', unsafe_allow_html=True)
        if st.button("Create a Quiz", use_container_width=True):
            go_to("AI Quiz")
            st.rerun()
    with col2:
        st.markdown('<div class="study-card"><h3>📚 PDF Notes</h3><p>Turn your study PDF into clear notes.</p></div>', unsafe_allow_html=True)
        if st.button("Make Notes", use_container_width=True):
            go_to("PDF Notes")
            st.rerun()
    with col3:
        st.markdown('<div class="study-card"><h3>💬 Study Chat</h3><p>Ask questions and learn step by step.</p></div>', unsafe_allow_html=True)
        if st.button("Ask AI", use_container_width=True):
            go_to("Study Chat")
            st.rerun()
    st.subheader("Recent Activity")
    st.info(st.session_state.last_activity)

elif st.session_state.page == "AI Quiz":
    show_heading("📝 AI Quiz", "Create practice questions for any subject.")
    topic = st.text_input("Enter topic", placeholder="Example: Semiconductor diodes")
    col1, col2 = st.columns(2)
    with col1:
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard", "Mixed"])
        question_type = st.selectbox("Question type", ["MCQ", "Short Answer", "Mixed"])
    with col2:
        count = st.selectbox("Number of questions", [5, 10, 20, 30, 40, 50, 75, 100], index=2)
        language = st.selectbox("Language", ["English", "Simple Hindi", "Hinglish"])
    instructions = st.text_area("Extra instructions (optional)", placeholder="Example: Focus on AKTU exam questions")
    if st.button("Generate Quiz", type="primary", use_container_width=True):
        if not topic.strip():
            st.warning("Pehle topic enter karo.")
        else:
            all_questions = []
            progress = st.progress(0)
            status = st.empty()
            for start in range(0, count, 10):
                current_count = min(10, count - start)
                status.write(f"Generating questions {start + 1}–{start + current_count}...")
                prompt = f"""
Create exactly {current_count} {question_type} practice questions on: {topic}.
Difficulty: {difficulty}. Language: {language}.
Extra instructions: {instructions or "None"}.
Number these questions from {start + 1} to {start + current_count}.
For MCQs, give four options (A, B, C, D) and the correct answer.
For short-answer questions, give a short model answer.
For Mixed, include both types.
Do not add an introduction or extra questions. Avoid repeating concepts.
"""
                try:
                    result = ask_ai(prompt, max_tokens=3500)
                    if not result:
                        break
                    all_questions.append(result)
                except Exception as e:
                    st.error(f"Quiz generate nahi ho paya: {e}")
                    break
                progress.progress(min(1.0, (start + current_count) / count))
            status.empty()
            if all_questions:
                st.session_state.last_quiz = "\n\n".join(all_questions)
                st.session_state.quiz_topic = topic
                st.session_state.generated_quizzes += 1
                st.session_state.quiz_history.append({
                    "topic": topic, "questions": count, "difficulty": difficulty,
                    "date": datetime.now().strftime("%d-%m-%Y %I:%M %p")
                })
                st.session_state.last_activity = "Created a quiz on " + topic
                st.success("Quiz ready!")
    if st.session_state.last_quiz:
        st.subheader("Your Quiz")
        st.markdown(st.session_state.last_quiz)
        st.download_button("Download Quiz as TXT", st.session_state.last_quiz, file_name="study_quiz.txt", mime="text/plain")

elif st.session_state.page == "PDF Notes":
    show_heading("📚 PDF Notes", "Upload a PDF and turn it into revision notes.")
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
    if uploaded_file is not None:
        try:
            pdf_text = extract_pdf_text(uploaded_file)
            st.session_state.pdf_text = pdf_text
            st.write(f"Extracted {len(pdf_text)} characters from the PDF.")
            with st.expander("Preview PDF text"):
                st.text(pdf_text[:2500] if pdf_text else "No readable text found.")
        except Exception as e:
            st.error(f"PDF read nahi ho payi: {e}")

    if st.session_state.pdf_text:
        col1, col2 = st.columns(2)
        with col1:
            note_style = st.selectbox("Notes style", ["Short Notes", "Detailed Notes", "Key Points", "Summary Notes", "Question–Answer Notes"])
            detail = st.select_slider("Detail level", options=["Concise", "Balanced", "Detailed"], value="Balanced")
        with col2:
            language = st.selectbox("Notes language", ["English", "Simple Hindi", "Hinglish"])
            extra = st.text_input("Extra instructions (optional)", placeholder="Example: Keep it exam-focused")
        if st.button("Generate Notes", type="primary", use_container_width=True):
            source_text = st.session_state.pdf_text[:26000]
            prompt = f"""
Make {note_style} from the source text below.
Detail level: {detail}. Language: {language}.
Extra instructions: {extra or "None"}.
Use clear headings, simple explanations, definitions, important formulas and examples when present.
Use bullet points starting with "- ". Put headings on separate lines starting with "# ".
For Question–Answer Notes, write useful questions and answers.
Keep facts faithful to the source. Do not invent information.
SOURCE TEXT:
{source_text}
"""
            with st.spinner("Making your notes..."):
                try:
                    notes = ask_ai(prompt, max_tokens=6000, temperature=0.3)
                    if notes:
                        st.session_state.last_notes = notes
                        st.session_state.notes_created += 1
                        st.session_state.notes_history.append({
                            "style": note_style, "date": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
                            "words": len(notes.split())
                        })
                        st.session_state.last_activity = "Created " + note_style.lower()
                        st.success("Notes ready!")
                        if len(st.session_state.pdf_text) > 26000:
                            st.info("Long PDF hai, isliye AI ko pehle 26,000 characters diye gaye hain.")
                except Exception as e:
                    st.error(f"Notes generate nahi ho paye: {e}")
    if st.session_state.last_notes:
        st.subheader("Your Notes")
        st.markdown(st.session_state.last_notes)
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("Download Notes as TXT", st.session_state.last_notes, file_name="study_notes.txt", mime="text/plain", use_container_width=True)
        with col2:
            try:
                pdf_data = make_pdf(st.session_state.last_notes)
                st.download_button("Download Notes as PDF", pdf_data, file_name="study_notes.pdf", mime="application/pdf", use_container_width=True)
            except Exception as e:
                st.error(f"PDF create nahi ho payi: {e}")

elif st.session_state.page == "Study Chat":
    show_heading("💬 Study Chat", "Ask questions and get step-by-step explanations.")
    if st.button("Start New Chat"):
        st.session_state.chat_messages = []
        st.rerun()
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    question = st.chat_input("Ask a study question...")
    if question:
        st.session_state.chat_messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        messages = [{"role": "system", "content": "You are Study Buddy AI, a patient study helper. Explain concepts clearly in simple language, use steps and examples when helpful, and help the student learn."}]
        messages.extend(st.session_state.chat_messages[-10:])
        try:
            client = get_client()
            if client:
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response = client.chat.completions.create(
                            model=MODEL, messages=messages, max_tokens=2500, temperature=0.4
                        )
                        answer = response.choices[0].message.content or "I couldn't create an answer."
                    st.markdown(answer)
                st.session_state.chat_messages.append({"role": "assistant", "content": answer})
                st.session_state.last_activity = "Used Study Chat"
        except Exception as e:
            st.error(f"Chat mein error aaya: {e}")

elif st.session_state.page == "Performance":
    show_heading("📊 Performance", "Check your activity in this session.")
    col1, col2, col3 = st.columns(3)
    col1.metric("Quizzes Created", st.session_state.generated_quizzes)
    col2.metric("Notes Created", st.session_state.notes_created)
    col3.metric("Chat Messages", len(st.session_state.chat_messages))
    left, right = st.columns(2)
    with left:
        st.subheader("Quiz History")
        if st.session_state.quiz_history:
            for item in reversed(st.session_state.quiz_history):
                st.markdown(f"**{item['topic']}**")
                st.caption(f"{item['questions']} questions · {item['difficulty']} · {item['date']}")
                st.divider()
        else:
            st.info("Abhi koi quiz history nahi hai.")
    with right:
        st.subheader("Notes History")
        if st.session_state.notes_history:
            for item in reversed(st.session_state.notes_history):
                st.markdown(f"**{item['style']}**")
                st.caption(f"{item['words']} words · {item['date']}")
                st.divider()
        else:
            st.info("Abhi koi notes history nahi hai.")
    st.caption("History abhi current session mein save hoti hai.")

elif st.session_state.page == "Settings":
    show_heading("⚙️ Settings", "Manage your app session.")
    st.subheader("AI Configuration")
    st.write("Model:", MODEL)
    st.caption("API key Streamlit Secrets mein GROQ_API_KEY naam se honi chahiye.")
    st.divider()
    st.subheader("Clear Data")
    st.warning("Clearing data cannot be undone in this session.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear Quiz and Notes History", use_container_width=True):
            st.session_state.quiz_history = []
            st.session_state.notes_history = []
            st.session_state.generated_quizzes = 0
            st.session_state.notes_created = 0
            st.session_state.last_quiz = ""
            st.session_state.last_notes = ""
            st.success("Quiz aur notes history clear ho gayi.")
    with col2:
        if st.button("Clear Chat History", use_container_width=True):
            st.session_state.chat_messages = []
            st.success("Chat history clear ho gayi.")
    st.divider()
    st.subheader("About Study Buddy AI")
    st.write("Study Buddy AI helps students practise questions, make notes from PDFs and understand topics through chat.")

st.divider()
st.markdown("<p style='text-align:center;color:#718278;font-size:13px'>STUDY BUDDY AI · Learn at your own pace · Keep making progress</p>", unsafe_allow_html=True)
