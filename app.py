import streamlit as st
from groq import Groq
from pypdf import PdfReader
from io import BytesIO
from datetime import datetime
from html import escape
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

st.set_page_config(
    page_title="Study Buddy AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

MODEL = "openai/gpt-oss-20b"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #F4F7F2;
    --paper: #FFFFFF;
    --ink: #17372A;
    --green: #087F5B;
    --deep: #064E3B;
    --mint: #DDF3E5;
    --line: #DCE7DD;
    --muted: #718278;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: var(--bg);
    color: var(--ink);
}

#MainMenu, footer {
    visibility: hidden;
}

header[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1250px;
    padding: 1.3rem 2rem 3rem;
}

h1, h2, h3 {
    font-family: 'Manrope', sans-serif !important;
    color: var(--ink);
    letter-spacing: -1px;
}

p {
    line-height: 1.7;
}

hr {
    border-color: var(--line);
}

div.stButton > button {
    min-height: 44px;
    border-radius: 12px;
    border: 1px solid var(--line);
    font-weight: 700;
    background: white;
    color: var(--ink);
    transition: all .2s ease;
}

div.stButton > button:hover {
    border-color: var(--green);
    color: var(--green);
    background: #F0F8F1;
}

div.stButton > button[kind="primary"] {
    background: var(--green);
    color: white;
    border-color: var(--green);
}

div.stButton > button[kind="primary"]:hover {
    background: var(--deep);
    color: white;
}

.stTextInput input, .stTextArea textarea,
.stSelectbox div[data-baseweb="select"],
.stNumberInput input {
    border-radius: 11px !important;
}

[data-testid="stFileUploader"] {
    border: 1px dashed #91C5A0;
    border-radius: 16px;
    background: white;
    padding: 12px;
}

[data-testid="stChatMessage"] {
    background: white;
    border: 1px solid var(--line);
    border-radius: 15px;
}

[data-testid="stMetric"] {
    background: white;
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 17px;
}

[data-testid="stMetricValue"] {
    color: var(--green);
    font-family: 'Manrope', sans-serif;
}

.sb-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    border-bottom: 1px solid var(--line);
    padding: 5px 0 18px;
    margin-bottom: 22px;
}

.sb-brand {
    display: flex;
    align-items: center;
    gap: 12px;
}

.sb-logo {
    width: 46px;
    height: 46px;
    border-radius: 15px 15px 15px 4px;
    background: var(--green);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font: 800 22px 'Manrope', sans-serif;
    box-shadow: 0 6px 18px #087F5B25;
}

.sb-name {
    font: 800 18px 'Manrope', sans-serif;
    letter-spacing: -.7px;
    color: var(--ink);
}

.sb-tag {
    font-size: 9px;
    letter-spacing: 1.5px;
    color: var(--muted);
    margin-top: 4px;
}

.sb-status {
    color: var(--green);
    background: #EAF7ED;
    border: 1px solid #CBE6D0;
    border-radius: 30px;
    padding: 9px 12px;
    font-size: 10px;
    letter-spacing: .7px;
    white-space: nowrap;
}

.sb-hero {
    position: relative;
    overflow: hidden;
    background: linear-gradient(120deg, #103D32, #087F5B 72%, #15976C);
    border-radius: 25px;
    padding: 38px;
    color: white;
    min-height: 315px;
}

.sb-hero:after {
    content: "";
    position: absolute;
    width: 300px;
    height: 300px;
    border: 1px solid #FFFFFF35;
    border-radius: 50%;
    right: -100px;
    top: -150px;
    box-shadow: 0 0 0 35px #FFFFFF08,
                0 0 0 75px #FFFFFF06;
}

.sb-kicker {
    color: #C7EDB5;
    font-size: 10px;
    letter-spacing: 2px;
    font-weight: 700;
}

.sb-hero-title {
    position: relative;
    z-index: 1;
    font: 800 clamp(37px, 5vw, 62px)/1.08 'Manrope', sans-serif;
    letter-spacing: -3px;
    color: white;
    margin: 23px 0 15px;
}

.sb-hero-title span {
    color: #C7EDB5;
}

.sb-hero-copy {
    position: relative;
    z-index: 1;
    color: #E1F1E8;
    font-size: 14px;
    max-width: 530px;
    line-height: 1.9;
}

.sb-eyebrow {
    color: var(--green);
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.7px;
}

.sb-heading {
    font: 800 clamp(28px, 3vw, 40px)/1.2 'Manrope', sans-serif;
    letter-spacing: -1.8px;
    margin: 8px 0;
}

.sb-sub {
    color: var(--muted);
    font-size: 13px;
    line-height: 1.8;
}

.sb-section {
    margin: 30px 0 15px;
}

.sb-section-title {
    font: 800 24px 'Manrope', sans-serif;
    letter-spacing: -1px;
}

.sb-stat {
    background: white;
    border: 1px solid var(--line);
    border-radius: 17px;
    padding: 19px;
    min-height: 145px;
}

.sb-stat-label {
    color: var(--muted);
    font-size: 10px;
    letter-spacing: 1px;
    font-weight: 700;
}

.sb-stat-number {
    color: var(--green);
    font: 800 38px 'Manrope', sans-serif;
    letter-spacing: -2px;
    margin-top: 13px;
}

.sb-stat-caption {
    color: var(--muted);
    font-size: 11px;
    margin-top: 3px;
}

.sb-feature {
    background: white;
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 23px;
    min-height: 185px;
    margin-bottom: 10px;
}

.sb-feature-icon {
    display: inline-flex;
    width: 43px;
    height: 43px;
    align-items: center;
    justify-content: center;
    border-radius: 13px;
    background: var(--mint);
    font-size: 22px;
    margin-bottom: 17px;
}

.sb-feature-title {
    font: 800 20px 'Manrope', sans-serif;
    letter-spacing: -.7px;
}

.sb-feature-copy {
    color: var(--muted);
    font-size: 12px;
    line-height: 1.8;
    margin-top: 8px;
}

.sb-panel {
    background: white;
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 23px;
    margin-bottom: 14px;
}

.sb-panel-label {
    color: var(--green);
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.5px;
}

.sb-panel-title {
    font: 800 22px 'Manrope', sans-serif;
    letter-spacing: -.8px;
    margin: 8px 0;
}

.sb-side {
    background: #E2F2E5;
    color: var(--deep);
    border-radius: 19px;
    padding: 24px;
}

.sb-side-quote {
    font: 800 23px/1.4 'Manrope', sans-serif;
    letter-spacing: -.7px;
    margin: 15px 0;
}

.sb-footer {
    border-top: 1px solid var(--line);
    margin-top: 32px;
    padding-top: 16px;
    color: #819087;
    font-size: 9px;
    letter-spacing: 1px;
    display: flex;
    justify-content: space-between;
    gap: 10px;
}

@media(max-width: 700px) {
    .block-container {
        padding: .8rem 1rem 2rem;
    }
    .sb-hero {
        padding: 25px 22px;
        min-height: 300px;
    }
    .sb-hero-title {
        font-size: 39px;
        letter-spacing: -2px;
    }
    .sb-hero-copy {
        font-size: 12px;
    }
    .sb-name {
        font-size: 15px;
    }
    .sb-tag {
        font-size: 8px;
        letter-spacing: .8px;
    }
    .sb-status {
        font-size: 8px;
        padding: 8px;
    }
    .sb-stat {
        padding: 13px;
        min-height: 125px;
    }
    .sb-stat-number {
        font-size: 30px;
    }
    .sb-feature {
        padding: 18px;
        min-height: auto;
    }
    .sb-footer {
        flex-direction: column;
    }
}
</style>
""", unsafe_allow_html=True)


# ---------- SESSION STATE ----------

defaults = {
    "page": "Dashboard",
    "chat": [],
    "quiz_history": [],
    "notes_history": [],
    "last_quiz": "",
    "last_notes": "",
    "quiz_topic": "",
    "notes_title": "",
    "pdf_text": "",
    "activity": "Your learning journey starts here",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def get_client():
    try:
        key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        key = ""

    if not key:
        return None

    return Groq(api_key=key)


def ask_ai(prompt, max_tokens=3000, temperature=0.4, messages=None):
    client = get_client()

    if client is None:
        st.error(
            "GROQ_API_KEY is missing. Open Streamlit Cloud → "
            "App settings → Secrets and configure your key."
        )
        return None

    if messages is None:
        messages = [{"role": "user", "content": prompt}]

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    except Exception as error:
        st.error(f"AI request failed: {error}")
        return None


def page_header(number, title, description):
    st.markdown(f"""
    <div style="padding:10px 0 22px;border-bottom:1px solid #DCE7DD;margin-bottom:24px">
        <div class="sb-eyebrow">STUDY BUDDY AI / {escape(number)}</div>
        <div class="sb-heading">{escape(title)}</div>
        <div class="sb-sub">{escape(description)}</div>
    </div>
    """, unsafe_allow_html=True)


def section(label, title):
    st.markdown(f"""
    <div class="sb-section">
        <div class="sb-eyebrow">{escape(label)}</div>
        <div class="sb-section-title">{escape(title)}</div>
    </div>
    """, unsafe_allow_html=True)


def stat(label, value, caption):
    st.markdown(f"""
    <div class="sb-stat">
        <div class="sb-stat-label">{escape(label)}</div>
        <div class="sb-stat-number">{escape(str(value))}</div>
        <div class="sb-stat-caption">{escape(caption)}</div>
    </div>
    """, unsafe_allow_html=True)


def panel(label, title, description):
    st.markdown(f"""
    <div class="sb-panel">
        <div class="sb-panel-label">{escape(label)}</div>
        <div class="sb-panel-title">{escape(title)}</div>
        <div class="sb-sub">{escape(description)}</div>
    </div>
    """, unsafe_allow_html=True)


def make_pdf(content, title="Study Buddy AI Notes"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "SBTitle",
        parent=styles["Title"],
        textColor=colors.HexColor("#087F5B"),
        fontSize=22,
        leading=28,
        spaceAfter=18
    )
    body_style = ParagraphStyle(
        "SBBody",
        parent=styles["BodyText"],
        fontSize=10,
        leading=16,
        textColor=colors.HexColor("#24392E"),
        spaceAfter=8
    )

    story = [
        Paragraph(escape(title), title_style),
        Paragraph("Created with Study Buddy AI", styles["Normal"]),
        Spacer(1, 18)
    ]

    for line in content.splitlines():
        line = line.strip()

        if not line:
            story.append(Spacer(1, 5))
        elif line.startswith("#"):
            story.append(
                Paragraph(
                    escape(line.lstrip("#").strip()),
                    styles["Heading2"]
                )
            )
        elif line.startswith(("- ", "* ", "• ")):
            story.append(
                Paragraph("&#8226; " + escape(line[2:].strip()), body_style)
            )
        else:
            story.append(Paragraph(escape(line), body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# ---------- BRAND AND NAVIGATION ----------

st.markdown("""
<div class="sb-top">
    <div class="sb-brand">
        <div class="sb-logo">S.</div>
        <div>
            <div class="sb-name">Study Buddy AI</div>
            <div class="sb-tag">YOUR PERSONAL LEARNING SPACE</div>
        </div>
    </div>
    <div class="sb-status">✦ AI WORKSPACE</div>
</div>
""", unsafe_allow_html=True)

pages = [
    "Dashboard",
    "AI Quiz",
    "PDF Notes",
    "Study Chat",
    "Performance",
    "Settings"
]

st.session_state.page = st.radio(
    "Navigation",
    pages,
    index=pages.index(st.session_state.page),
    horizontal=True,
    label_visibility="collapsed",
    key="main_navigation"
)

st.markdown("---")


# ---------- DASHBOARD ----------

def dashboard():
    st.markdown("""
    <div class="sb-hero">
        <div class="sb-kicker">✦ YOUR PERSONAL AI STUDY SPACE</div>
        <div class="sb-hero-title">
            Make every study<br>session <span>count.</span>
        </div>
        <div class="sb-hero-copy">
            One workspace for smarter revision, clearer notes and better
            understanding. Learn at your own pace with your personal AI tutor.
        </div>
    </div>
    """, unsafe_allow_html=True)

    section("YOUR ACTIVITY / 01", "Your study overview")

    quiz_count = len(st.session_state.quiz_history)
    notes_count = len(st.session_state.notes_history)
    chat_count = sum(
        1 for message in st.session_state.chat if message["role"] == "user"
    )

    a, b, c = st.columns(3)

    with a:
        stat("QUIZ SETS", quiz_count, "Practice sets created")
    with b:
        stat("NOTES CREATED", notes_count, "Study resources prepared")
    with c:
        stat("QUESTIONS ASKED", chat_count, "Questions sent to your tutor")

    section("THE TOOLKIT / 02", "Choose your next move")

    a, b = st.columns(2)

    with a:
        st.markdown("""
        <div class="sb-feature">
            <div class="sb-feature-icon">✳</div>
            <div class="sb-feature-title">AI Quiz Lab</div>
            <div class="sb-feature-copy">
                Build topic-based questions, practise concepts and review
                answers with explanations.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open AI Quiz ↗", key="home_quiz", width="stretch"):
            st.session_state.page = "AI Quiz"
            st.rerun()

    with b:
        st.markdown("""
        <div class="sb-feature">
            <div class="sb-feature-icon">▤</div>
            <div class="sb-feature-title">Notes Studio</div>
            <div class="sb-feature-copy">
                Turn readable PDF material into structured notes for revision
                and download them as TXT or PDF.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open PDF Notes ↗", key="home_notes", width="stretch"):
            st.session_state.page = "PDF Notes"
            st.rerun()

    a, b = st.columns(2)

    with a:
        st.markdown("""
        <div class="sb-feature">
            <div class="sb-feature-icon">◉</div>
            <div class="sb-feature-title">Study Chat</div>
            <div class="sb-feature-copy">
                Ask doubts and explore difficult topics with clear,
                step-by-step explanations.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Study Chat ↗", key="home_chat", width="stretch"):
            st.session_state.page = "Study Chat"
            st.rerun()

    with b:
        st.markdown("""
        <div class="sb-feature">
            <div class="sb-feature-icon">↗</div>
            <div class="sb-feature-title">Growth Tracker</div>
            <div class="sb-feature-copy">
                Review your recent quizzes, notes and activity from the
                current session.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View Performance ↗", key="home_performance", width="stretch"):
            st.session_state.page = "Performance"
            st.rerun()

    section("LEARNING TRAIL / 03", "Your latest activity")
    panel("RECENT ACTIVITY", "Your learning journey",
          st.session_state.activity)

    st.markdown("""
    <div class="sb-footer">
        <span>STUDY BUDDY AI · PERSONAL LEARNING WORKSPACE</span>
        <span>LEARN WITH PURPOSE ↗</span>
    </div>
    """, unsafe_allow_html=True)


# ---------- AI QUIZ ----------

def ai_quiz():
    page_header(
        "01 / PRACTICE",
        "AI Quiz Lab",
        "Create practice questions around your subject, level and goals."
    )

    left, right = st.columns([1.2, 0.8])

    with left:
        panel("QUIZ CONFIGURATION", "Build your practice set",
              "Choose a topic and customise your revision session.")

        topic = st.text_input(
            "Topic or subject",
            placeholder="e.g. BJT, recursion, electrochemistry",
            key="quiz_topic_input"
        )
        difficulty = st.selectbox(
            "Difficulty", ["Easy", "Medium", "Hard", "Mixed"]
        )
        qtype = st.selectbox(
            "Question format", ["MCQ", "Short Answer", "Mixed"]
        )
        language = st.selectbox(
            "Language", ["Simple English", "Hindi", "Hinglish"]
        )
        count = st.select_slider(
            "Number of questions",
            options=[5, 10, 15, 20, 30, 40, 50],
            value=10
        )

        generate = st.button(
            "✳ Generate quiz",
            type="primary",
            width="stretch"
        )

    with right:
        st.markdown("""
        <div class="sb-side">
            <div class="sb-eyebrow">PRACTICE PRINCIPLE / 01</div>
            <div class="sb-side-quote">
                Test what you know. Discover what you can learn.
            </div>
            <div class="sb-sub">
                TOPIC-BASED · ADAPTABLE · REVISION-READY
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")
        panel("STUDY TIP", "Try before you reveal",
              "Attempt each question first, then read the answer and explanation.")

    if generate:
        if not topic.strip():
            st.warning("Please enter a topic first.")
        else:
            outputs = []
            remaining = count
            start = 1
            failed = False

            with st.spinner("Creating your practice set..."):
                while remaining > 0:
                    batch = min(10, remaining)

                    prompt = f"""
You are an accurate college-level tutor.
Create exactly {batch} questions about: {topic}
Difficulty: {difficulty}
Format: {qtype}
Language: {language}
Start numbering at {start}.

For MCQs, provide options A, B, C, D, the correct answer
and a short explanation.
For short answers, provide a clear model answer.
For mixed format, include both formats.
Keep formatting readable. No introduction.
Do not invent facts.
"""

                    result = ask_ai(prompt, max_tokens=4500)

                    if not result:
                        failed = True
                        break

                    outputs.append(result)
                    remaining -= batch
                    start += batch

            if outputs:
                combined = "\n\n".join(outputs)
                st.session_state.last_quiz = combined
                st.session_state.quiz_topic = topic
                st.session_state.quiz_history.append({
                    "topic": topic,
                    "count": count,
                    "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                    "content": combined
                })
                st.session_state.activity = f"Generated quiz: {topic}"

                if failed:
                    st.warning("Quiz partially generated. Available questions are shown.")
                else:
                    st.success("Your quiz is ready!")

    if st.session_state.last_quiz:
        section("GENERATED MATERIAL", st.session_state.quiz_topic)
        st.markdown(st.session_state.last_quiz)
        st.download_button(
            "Download quiz as TXT",
            data=st.session_state.last_quiz,
            file_name="study_buddy_quiz.txt",
            mime="text/plain",
            width="stretch"
        )


# ---------- PDF NOTES ----------

def pdf_notes():
    page_header(
        "02 / ORGANISE",
        "Notes Studio",
        "Convert readable PDF material into organised, student-friendly notes."
    )

    panel("DOCUMENT WORKSPACE", "Bring your study material",
          "Upload your PDF and choose how you want your notes organised.")

    uploaded = st.file_uploader("Upload study PDF", type=["pdf"])

    style = st.selectbox(
        "Notes format",
        [
            "Detailed notes with headings",
            "Exam revision notes",
            "Short summary",
            "Question and answer format",
            "Bullet-point notes"
        ]
    )
    language = st.selectbox(
        "Output language", ["Simple English", "Hindi", "Hinglish"]
    )

    if uploaded:
        try:
            reader = PdfReader(uploaded)
            extracted = "\n".join(
                page.extract_text() or "" for page in reader.pages
            ).strip()

            if extracted:
                st.session_state.pdf_text = extracted
                st.session_state.notes_title = uploaded.name
                st.success(f"PDF ready · {len(reader.pages)} pages")
            else:
                st.warning(
                    "Selectable text was not found. Scanned PDFs may need OCR."
                )
        except Exception as error:
            st.error(f"Could not read PDF: {error}")

    if st.button(
        "▤ Create notes",
        type="primary",
        width="stretch"
    ):
        if not st.session_state.pdf_text:
            st.warning("Please upload a readable PDF first.")
        else:
            prompt = f"""
You are an educational note-making assistant.
Create notes only from the source material below.

Style: {style}
Language: {language}

Use headings, subheadings and bullet points.
Preserve key definitions, formulas, examples and facts.
Explain concepts in student-friendly language.
Do not invent details or claim to cover unseen material.

SOURCE:
{st.session_state.pdf_text[:26000]}
"""
            with st.spinner("Organising your notes..."):
                notes = ask_ai(prompt, max_tokens=6000)

            if notes:
                st.session_state.last_notes = notes
                st.session_state.notes_history.append({
                    "title": st.session_state.notes_title or "Study Notes",
                    "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                    "content": notes
                })
                st.session_state.activity = "Created PDF study notes"
                st.success("Your notes are ready!")

    if st.session_state.last_notes:
        section("YOUR DOCUMENT", "Ready for revision")
        st.markdown(st.session_state.last_notes)

        a, b = st.columns(2)

        with a:
            st.download_button(
                "Download TXT",
                data=st.session_state.last_notes,
                file_name="study_buddy_notes.txt",
                mime="text/plain",
                width="stretch"
            )

        with b:
            try:
                pdf_data = make_pdf(st.session_state.last_notes)
                st.download_button(
                    "Download PDF",
                    data=pdf_data,
                    file_name="study_buddy_notes.pdf",
                    mime="application/pdf",
                    width="stretch"
                )
            except Exception as error:
                st.error(f"PDF export failed: {error}")


# ---------- STUDY CHAT ----------

def study_chat():
    page_header(
        "03 / UNDERSTAND",
        "Study Chat",
        "Ask questions, explore examples and work through difficult concepts."
    )

    st.markdown("""
    <div class="sb-panel">
        <div class="sb-panel-label">CONVERSATION SPACE</div>
        <div class="sb-panel-title">Curiosity starts here.</div>
        <div class="sb-sub">
            Ask one question at a time for focused, clear explanations.
        </div>
    </div>
    """, unsafe_allow_html=True)

    for message in st.session_state.chat:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask your study question...")

    if prompt:
        st.session_state.chat.append({
            "role": "user", "content": prompt
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        messages = [{
            "role": "system",
            "content": (
                "You are Study Buddy AI, a patient and accurate study tutor. "
                "Explain clearly in the user's language. Show calculation "
                "steps where needed and do not invent facts."
            )
        }]
        messages.extend(st.session_state.chat[-12:])

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = ask_ai(
                    "",
                    max_tokens=3000,
                    messages=messages
                )

            if answer:
                st.markdown(answer)
                st.session_state.chat.append({
                    "role": "assistant", "content": answer
                })
                st.session_state.activity = "Asked a question in Study Chat"

    if st.session_state.chat:
        if st.button("Clear chat", width="stretch"):
            st.session_state.chat = []
            st.rerun()


# ---------- PERFORMANCE ----------

def performance():
    page_header(
        "04 / REFLECT",
        "Your progress",
        "Review the quizzes, notes and study activity created in this session."
    )

    quiz_count = len(st.session_state.quiz_history)
    notes_count = len(st.session_state.notes_history)
    chat_count = sum(
        1 for message in st.session_state.chat
        if message["role"] == "user"
    )

    a, b, c = st.columns(3)
    with a:
        st.metric("Quiz sessions", quiz_count)
    with b:
        st.metric("Notes created", notes_count)
    with c:
        st.metric("Questions asked", chat_count)

    section("ACTIVITY / 01", "Your latest work")
    panel("MOST RECENT", st.session_state.activity,
          "History is stored in the current session and may reset when the session restarts.")

    section("PRACTICE / 02", "Quiz history")

    if st.session_state.quiz_history:
        for i, item in enumerate(reversed(st.session_state.quiz_history[-10:])):
            with st.expander(
                f"{item['topic']} · {item['count']} questions · {item['date']}"
            ):
                st.markdown(item["content"])
                st.download_button(
                    "Download quiz",
                    data=item["content"],
                    file_name="study_buddy_quiz.txt",
                    mime="text/plain",
                    key=f"quiz_history_{i}"
                )
    else:
        st.info("Your quiz history will appear here.")

    section("RESOURCES / 03", "Notes history")

    if st.session_state.notes_history:
        for i, item in enumerate(reversed(st.session_state.notes_history[-10:])):
            with st.expander(f"{item['title']} · {item['date']}"):
                st.markdown(item["content"])
                st.download_button(
                    "Download notes",
                    data=item["content"],
                    file_name="study_buddy_notes.txt",
                    mime="text/plain",
                    key=f"notes_history_{i}"
                )
    else:
        st.info("Your notes history will appear here.")


# ---------- SETTINGS ----------

def settings():
    page_header(
        "05 / SETTINGS",
        "Your workspace",
        "Review app information and manage your current session."
    )

    panel(
        "PRODUCT IDENTITY",
        "Study Buddy AI",
        "An AI learning workspace for quizzes, PDF notes and study conversations."
    )

    panel(
        "AI MODEL",
        MODEL,
        "Powered by Groq. Your API key must be configured privately in Streamlit Secrets."
    )

    panel(
        "SESSION DATA",
        "About your history",
        "Quiz history, notes and chat messages are kept in the active session. "
        "They are not a permanent database and may reset when the session restarts."
    )

    section("DANGER ZONE", "Clear session history")

    confirm = st.checkbox(
        "I understand this will clear my current quiz, notes and chat history."
    )

    if st.button(
        "Clear session data",
        type="primary",
        width="stretch"
    ):
        if not confirm:
            st.warning("Please confirm before clearing session data.")
        else:
            for key, value in {
                "chat": [],
                "quiz_history": [],
                "notes_history": [],
                "last_quiz": "",
                "last_notes": "",
                "quiz_topic": "",
                "notes_title": "",
                "pdf_text": "",
                "activity": "Your learning journey starts here",
            }.items():
                st.session_state[key] = value

            st.success("Current session data cleared.")
            st.rerun()


# ---------- PAGE ROUTER ----------

if st.session_state.page == "Dashboard":
    dashboard()
elif st.session_state.page == "AI Quiz":
    ai_quiz()
elif st.session_state.page == "PDF Notes":
    pdf_notes()
elif st.session_state.page == "Study Chat":
    study_chat()
elif st.session_state.page == "Performance":
    performance()
elif st.session_state.page == "Settings":
    settings()

st.markdown("""
<div class="sb-footer">
    <span>STUDY BUDDY AI</span>
    <span>LEARN · PRACTISE · GROW</span>
</div>
""", unsafe_allow_html=True)
