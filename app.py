import streamlit as st
from groq import Groq
from pypdf import PdfReader
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from xml.sax.saxutils import escape

st.set_page_config(
    page_title="Study Buddy AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

MODEL = "openai/gpt-oss-20b"

DEFAULTS = {
    "page": "Dashboard",
    "generated_quizzes": 0,
    "notes_created": 0,
    "chat_messages": [],
    "last_quiz": "",
    "last_notes": "",
    "last_activity": "Ready to study",
    "quiz_history": [],
    "notes_history": [],
    "pdf_text": "",
    "quiz_topic": "",
    "quiz_partial": False
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --green: #087f5b;
    --green-dark: #104c46;
    --mint: #b5f4d8;
    --ink: #17233c;
    --muted: #75819a;
    --line: #e6ebf2;
}

.stApp {
    background:
        radial-gradient(ellipse at 0% 0%, rgba(18,168,121,.07), transparent 32%),
        radial-gradient(ellipse at 100% 5%, rgba(42,144,113,.05), transparent 28%),
        #f5f7fb;
    color: var(--ink);
    font-family: 'DM Sans', sans-serif;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

h1, h2, h3, h4 {
    font-family: 'Manrope', sans-serif !important;
    color: var(--ink);
    letter-spacing: -.6px;
}

.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #123b38 0%, #104c46 60%, #087f5b 100%);
    border-right: 1px solid rgba(255,255,255,.12);
}

[data-testid="stSidebar"] * {
    color: #f3fff9 !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    padding: 10px 12px;
    border-radius: 12px;
    transition: .2s ease;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(255,255,255,.12);
}

[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,.17);
}

.brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 3px 25px;
}

.brand-icon {
    width: 49px;
    height: 49px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 25px;
    background: linear-gradient(135deg, #a8f4d2, #36c996);
    box-shadow: 0 8px 24px rgba(0,0,0,.14);
}

.brand-name {
    font-family: 'Manrope', sans-serif;
    font-size: 18px;
    font-weight: 800;
    line-height: 1.3;
}

.brand-caption {
    font-size: 10px;
    color: #b7e5d4;
    letter-spacing: 1.3px;
    text-transform: uppercase;
    margin-top: 4px;
}

.hero {
    position: relative;
    overflow: hidden;
    padding: 36px;
    border-radius: 27px;
    background:
        radial-gradient(ellipse at 95% 0%, rgba(164,255,213,.17), transparent 35%),
        linear-gradient(120deg, #153e3e 0%, #116c58 58%, #128568 100%);
    box-shadow: 0 18px 45px rgba(16,75,66,.15);
    margin-bottom: 25px;
}

.hero:after {
    content: "";
    position: absolute;
    width: 270px;
    height: 270px;
    border: 1px solid rgba(255,255,255,.12);
    border-radius: 50%;
    right: -65px;
    top: -100px;
    box-shadow: 0 0 0 35px rgba(255,255,255,.035),
                0 0 0 70px rgba(255,255,255,.025);
    pointer-events: none;
}

.hero h1 {
    color: #ffffff !important;
    font-size: clamp(29px, 3.7vw, 47px);
    line-height: 1.18;
    font-weight: 800;
    margin: 17px 0 14px;
    letter-spacing: -1.2px;
}

.hero p {
    color: #d7eee5;
    font-size: 15px;
    line-height: 1.8;
    max-width: 650px;
}

.eyebrow {
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2px;
    color: #9cf0cf;
    text-transform: uppercase;
}

.hero-pill {
    display: inline-block;
    padding: 7px 12px;
    border: 1px solid rgba(255,255,255,.23);
    background: rgba(255,255,255,.09);
    border-radius: 30px;
    color: #f0fff8;
    font-size: 11px;
    letter-spacing: .5px;
}

.section-title {
    font-family: 'Manrope', sans-serif;
    font-weight: 800;
    font-size: 22px;
    margin: 27px 0 5px;
    color: #17233c;
}

.section-subtitle {
    font-size: 13px;
    color: #75819a;
    margin-bottom: 18px;
}

.metric-card {
    background: #ffffff;
    border: 1px solid #e6ebf2;
    border-radius: 20px;
    padding: 21px;
    min-height: 142px;
    box-shadow: 0 5px 22px rgba(30,48,80,.035);
    transition: transform .22s, box-shadow .22s;
}

.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 28px rgba(30,48,80,.08);
    border-color: #c6e9da;
}

.metric-icon {
    font-size: 23px;
    margin-bottom: 12px;
}

.metric-value {
    font-family: 'Manrope', sans-serif;
    font-size: 31px;
    font-weight: 800;
    color: #163d37;
    line-height: 1.2;
}

.metric-label {
    color: #75819a;
    font-size: 12px;
    margin-top: 7px;
}

.feature-card {
    min-height: 190px;
    padding: 23px;
    border: 1px solid #e6ebf2;
    background: #ffffff;
    border-radius: 21px;
    box-shadow: 0 5px 20px rgba(30,48,80,.035);
    transition: transform .22s, box-shadow .22s;
}

.feature-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 13px 30px rgba(30,48,80,.075);
    border-color: #c5e9da;
}

.feature-icon {
    font-size: 30px;
    margin-bottom: 14px;
}

.feature-card h3 {
    font-size: 17px;
    margin-bottom: 8px;
    color: #17233c;
}

.feature-card p {
    color: #75819a;
    font-size: 13px;
    line-height: 1.7;
}

.panel {
    padding: 25px;
    border-radius: 21px;
    background: #ffffff;
    border: 1px solid #e6ebf2;
    box-shadow: 0 6px 24px rgba(30,48,80,.035);
    margin-bottom: 18px;
}

.panel-title {
    font-family: 'Manrope', sans-serif;
    font-size: 19px;
    font-weight: 800;
    color: #17233c;
    margin-bottom: 5px;
}

.panel-subtitle {
    color: #75819a;
    font-size: 13px;
    margin-bottom: 20px;
}

.status-chip {
    display: inline-block;
    padding: 6px 11px;
    border-radius: 30px;
    font-size: 10px;
    font-weight: 800;
    background: #e6f8f0;
    color: #087f5b;
    letter-spacing: .7px;
}

.stButton > button {
    border-radius: 12px;
    min-height: 43px;
    font-weight: 700;
    border: 1px solid #e0e8e8;
    transition: .2s;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(110deg, #087f5b, #12a879);
    color: white;
    border: 0;
    box-shadow: 0 6px 18px rgba(8,127,91,.17);
}

.stButton > button:hover {
    transform: translateY(-1px);
    border-color: #12a879;
}

.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] {
    border-radius: 11px !important;
}

[data-testid="stFileUploader"] {
    background: #f8fbfa;
    border: 1px dashed #b8d8ce;
    border-radius: 15px;
    padding: 10px;
}

[data-testid="stChatMessage"] {
    background: #ffffff;
    border: 1px solid #e8edf4;
    border-radius: 17px;
    padding: 12px;
    margin-bottom: 12px;
}

div[data-testid="stMetric"] {
    background: #ffffff;
    padding: 15px;
    border: 1px solid #e6ebf2;
    border-radius: 15px;
}

.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #087f5b, #28c79a);
}

hr {
    border-color: #e6ebf2;
}

.footer {
    text-align: center;
    color: #8792a7;
    font-size: 11px;
    padding: 28px 0 0;
    letter-spacing: .5px;
}

@media (max-width: 700px) {
    .block-container {
        padding-top: 1rem;
    }

    .hero {
        padding: 24px 20px;
        border-radius: 20px;
    }

    .panel {
        padding: 18px;
    }

    .metric-card {
        padding: 16px;
    }

    .feature-card {
        min-height: auto;
    }
}
</style>
""", unsafe_allow_html=True)


def get_client():
    try:
        api_key = st.secrets.get("GROQ_API_KEY", "")
        if not api_key:
            st.error("GROQ_API_KEY missing hai. Streamlit Cloud → Settings → Secrets mein API key add karo.")
            return None
        return Groq(api_key=api_key)
    except Exception as e:
        st.error(f"AI setup error: {e}")
        return None


def ask_ai(prompt, max_tokens=5000, temperature=0.4):
    client = get_client()
    if client is None:
        return None
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"AI request failed: {e}")
        return None


def extract_pdf_text(file):
    try:
        reader = PdfReader(file)
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    except Exception as e:
        st.error(f"PDF read error: {e}")
        return ""


def make_pdf(text):
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
    styles.add(ParagraphStyle(
        name="BrandTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=26,
        textColor=colors.HexColor("#087f5b"),
        alignment=TA_CENTER,
        spaceAfter=20
    ))
    styles.add(ParagraphStyle(
        name="NoteHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#087f5b"),
        spaceBefore=12,
        spaceAfter=7
    ))
    styles.add(ParagraphStyle(
        name="NoteBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        spaceAfter=7
    ))

    story = [Paragraph("STUDY BUDDY AI", styles["BrandTitle"])]

    for line in text.splitlines():
        line = line.strip()

        if not line:
            story.append(Spacer(1, 5))
        elif line.startswith("#"):
            story.append(
                Paragraph(
                    escape(line.lstrip("#").strip()),
                    styles["NoteHeading"]
                )
            )
        elif line.startswith(("- ", "* ", "• ")):
            story.append(
                Paragraph(
                    "&#8226; " + escape(line[2:].strip()),
                    styles["NoteBody"]
                )
            )
        else:
            story.append(Paragraph(escape(line), styles["NoteBody"]))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def show_heading(title, subtitle):
    st.markdown(f"""
    <div style="margin-bottom:24px">
      <div class="eyebrow" style="color:#087f5b">STUDY BUDDY AI / WORKSPACE</div>
      <h1 style="font-size:32px;margin:9px 0 6px">{escape(title)}</h1>
      <div style="color:#75819a;font-size:14px">{escape(subtitle)}</div>
    </div>
    """, unsafe_allow_html=True)


def metric_card(icon, value, label):
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-icon">{icon}</div>
      <div class="metric-value">{value}</div>
      <div class="metric-label">{escape(label)}</div>
    </div>
    """, unsafe_allow_html=True)


def feature_card(icon, title, description):
    st.markdown(f"""
    <div class="feature-card">
      <div class="feature-icon">{icon}</div>
      <h3>{escape(title)}</h3>
      <p>{escape(description)}</p>
    </div>
    """, unsafe_allow_html=True)


with st.sidebar:
    st.markdown("""
    <div class="brand">
      <div class="brand-icon">🎓</div>
      <div>
        <div class="brand-name">Study Buddy AI</div>
        <div class="brand-caption">Your AI Study Companion</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div style="font-size:10px;letter-spacing:1.8px;color:#b7e5d4;margin:8px 0 10px">NAVIGATION</div>',
        unsafe_allow_html=True
    )

    pages = [
        "Dashboard",
        "AI Quiz",
        "PDF Notes",
        "Study Chat",
        "Performance",
        "Settings"
    ]

    selected = st.radio(
        "Navigation",
        pages,
        index=pages.index(st.session_state.page),
        label_visibility="collapsed"
    )
    st.session_state.page = selected

    st.markdown("---")
    st.markdown("""
    <div style="padding:15px;background:rgba(255,255,255,.08);
    border:1px solid rgba(255,255,255,.12);border-radius:15px">
      <div style="font-size:12px;font-weight:800">✦ YOUR AI STUDY SPACE</div>
      <div style="font-size:11px;color:#c2e6d8;margin-top:7px;line-height:1.7">
        Learn smarter. Practise better. Make every study session count.
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.caption("Powered by Groq AI")


if st.session_state.page == "Dashboard":

    st.markdown("""
    <div class="hero">
      <div class="hero-pill">✦ YOUR PERSONAL AI STUDY SPACE</div>
      <div style="height:16px"></div>
      <div class="eyebrow">LEARN SMARTER · GROW FASTER</div>
      <h1>Make every study<br>session count.</h1>
      <p>Your personal AI workspace for quizzes, clear notes and doubt solving. Turn study time into real progress.</p>
      <div class="status-chip">✦ BUILT FOR YOUR LEARNING JOURNEY</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Your study overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Your learning activity at a glance.</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card("🧠", st.session_state.generated_quizzes, "Quizzes generated")

    with c2:
        metric_card("📚", st.session_state.notes_created, "Notes created")

    with c3:
        metric_card("💬", len(st.session_state.chat_messages), "Chat messages")

    st.markdown('<div class="section-title">Explore your AI toolkit</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Everything you need to study smarter, in one place.</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        feature_card("🧩", "AI Quiz Studio", "Practise a topic with AI-generated questions and answers.")
        st.markdown("<div style='height:9px'></div>", unsafe_allow_html=True)
        if st.button("Create a quiz →", key="dash_quiz", type="primary", use_container_width=True):
            st.session_state.page = "AI Quiz"
            st.rerun()

    with c2:
        feature_card("📄", "PDF Notes Studio", "Convert your study PDF into organised, readable notes.")
        st.markdown("<div style='height:9px'></div>", unsafe_allow_html=True)
        if st.button("Make notes →", key="dash_notes", type="primary", use_container_width=True):
            st.session_state.page = "PDF Notes"
            st.rerun()

    with c3:
        feature_card("💬", "Your AI Tutor", "Ask questions and understand difficult concepts step by step.")
        st.markdown("<div style='height:9px'></div>", unsafe_allow_html=True)
        if st.button("Ask a doubt →", key="dash_chat", type="primary", use_container_width=True):
            st.session_state.page = "Study Chat"
            st.rerun()

    st.markdown('<div class="section-title">Recent activity</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="panel">
      <span class="status-chip">● SESSION STATUS</span>
      <div style="font-size:17px;font-weight:800;color:#17233c;margin-top:13px">{escape(st.session_state.last_activity)}</div>
      <div style="color:#75819a;font-size:12px;margin-top:7px">Your activity is tracked while this app session is active.</div>
    </div>
    """, unsafe_allow_html=True)


elif st.session_state.page == "AI Quiz":

    show_heading("AI Quiz Studio", "Create a personalised practice quiz for your next study session.")

    st.markdown("""
    <div class="panel">
      <div class="panel-title">Design your quiz</div>
      <div class="panel-subtitle">Choose your topic, difficulty and preferred question format.</div>
    """, unsafe_allow_html=True)

    topic = st.text_input(
        "Study topic",
        placeholder="e.g. BJT, C Programming, Data Structures"
    )

    c1, c2 = st.columns(2)

    with c1:
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard", "Mixed"])
        question_type = st.selectbox("Question format", ["MCQ", "Short Answer", "Mixed"])

    with c2:
        question_count = st.selectbox(
            "Number of questions",
            [5, 10, 20, 30, 40, 50, 75, 100],
            index=2
        )
        language = st.selectbox("Answer language", ["English", "Simple Hindi", "Hinglish"])

    extra_instructions = st.text_input(
        "Extra instructions (optional)",
        placeholder="e.g. Include important exam concepts and formulas"
    )

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("✦ Generate my quiz", type="primary", use_container_width=True):

        if not topic.strip():
            st.warning("Pehle study topic enter karo.")
        else:
            batch_size = 10
            batches = (question_count + batch_size - 1) // batch_size
            generated_parts = []

            progress = st.progress(0)
            status = st.empty()

            st.session_state.quiz_partial = False

            for batch_index in range(batches):

                start_num = batch_index * batch_size + 1
                end_num = min((batch_index + 1) * batch_size, question_count)
                current_count = end_num - start_num + 1

                status.info(f"Generating questions {start_num}–{end_num} of {question_count}...")

                prompt = f"""
You are an expert academic tutor.

Topic: {topic}
Difficulty: {difficulty}
Question format: {question_type}
Language: {language}
Question numbers: {start_num} to {end_num}
Number of questions required: {current_count}
Additional instructions: {extra_instructions or "None"}

Instructions:
1. Generate exactly {current_count} different questions.
2. Number the questions from {start_num} to {end_num}.
3. For MCQs, provide four options A, B, C and D.
4. Mark the correct answer clearly.
5. For short answers, provide a useful model answer.
6. For mixed format, include both MCQs and short-answer questions.
7. Add a short explanation where useful.
8. Cover different concepts and avoid repeating questions.
9. Keep all information accurate and relevant to the topic.
10. Use readable headings and spacing.
11. Do not add a long introduction.
"""

                result = ask_ai(prompt, max_tokens=5000, temperature=0.4)

                if not result:
                    st.session_state.quiz_partial = bool(generated_parts)
                    break

                generated_parts.append(result)
                progress.progress(len(generated_parts) / batches)

            status.empty()
            progress.empty()

            if generated_parts:
                quiz_text = "\n\n".join(generated_parts)

                st.session_state.last_quiz = quiz_text
                st.session_state.quiz_topic = topic
                st.session_state.generated_quizzes += 1

                st.session_state.quiz_history.insert(0, {
                    "topic": topic,
                    "questions_requested": question_count,
                    "batches_generated": len(generated_parts),
                    "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                    "difficulty": difficulty,
                    "complete": not st.session_state.quiz_partial
                })

                st.session_state.last_activity = f"Created a quiz on {topic}"

                if st.session_state.quiz_partial:
                    st.warning(
                        f"Quiz partially generated: {len(generated_parts)} of {batches} batches completed. Generated questions are available below."
                    )
                else:
                    st.success(f"Quiz generated successfully! Requested questions: {question_count}")

            else:
                st.error("Quiz generate nahi ho paya. API key, connection ya provider limits check karo.")

    if st.session_state.last_quiz:
        st.markdown('<div class="section-title">Your generated quiz</div>', unsafe_allow_html=True)
        st.caption(f"Topic: {st.session_state.quiz_topic}")
        st.markdown(st.session_state.last_quiz)

        st.download_button(
            "⬇️ Download quiz as TXT",
            data=st.session_state.last_quiz,
            file_name="study_buddy_ai_quiz.txt",
            mime="text/plain",
            use_container_width=True
        )


elif st.session_state.page == "PDF Notes":

    show_heading("PDF Notes Studio", "Turn your study material into clear, structured revision notes.")

    st.markdown("""
    <div class="panel">
      <div class="panel-title">Upload your study material</div>
      <div class="panel-subtitle">Upload a text-based PDF to create your notes.</div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

    if uploaded_file is not None:
        pdf_text = extract_pdf_text(uploaded_file)

        if pdf_text:
            st.session_state.pdf_text = pdf_text
            st.success(f"PDF loaded successfully · {len(pdf_text.split())} words detected.")

            with st.expander("Preview extracted text"):
                st.text(pdf_text[:3000])

                if len(pdf_text) > 3000:
                    st.caption("Preview shortened. The notes generator can use the extracted text within its processing limit.")

        else:
            st.warning("Readable text nahi mila. Scanned PDF ke liye OCR ki zaroorat ho sakti hai.")

    note_style = st.selectbox(
        "Notes style",
        [
            "Short Notes",
            "Detailed Notes",
            "Key Points",
            "Summary Notes",
            "Question–Answer Notes"
        ]
    )

    detail_level = st.select_slider(
        "Detail level",
        options=["Concise", "Balanced", "Detailed"],
        value="Balanced"
    )

    note_language = st.selectbox("Notes language", ["English", "Simple Hindi", "Hinglish"])

    note_instructions = st.text_input(
        "Special instructions (optional)",
        placeholder="e.g. Include definitions, formulas and exam questions"
    )

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("✦ Generate study notes", type="primary", use_container_width=True):

        if not st.session_state.pdf_text:
            st.warning("Pehle readable PDF upload karo.")
        else:
            source_text = st.session_state.pdf_text[:26000]

            prompt = f"""
You are an expert academic note-maker.

Create study notes from the supplied source.

Notes style: {note_style}
Detail level: {detail_level}
Language: {note_language}
Special instructions: {note_instructions or "None"}

Requirements:
1. Cover the important concepts in the supplied source.
2. Use clear headings and subheadings.
3. Explain ideas in student-friendly language.
4. Preserve important definitions, formulas, symbols and examples.
5. Use bullet points and numbered steps where useful.
6. Do not invent facts that are not supported by the source.
7. For Question–Answer Notes, write questions followed by answers.
8. For Key Points, use concise bullet points.
9. Make the notes useful for revision and examinations.
10. If the source is incomplete, mention the limitation.

SOURCE TEXT:
{source_text}
"""

            with st.spinner("Analysing your PDF and creating notes..."):
                notes = ask_ai(prompt, max_tokens=6000, temperature=0.3)

            if notes:
                st.session_state.last_notes = notes
                st.session_state.notes_created += 1

                st.session_state.notes_history.insert(0, {
                    "style": note_style,
                    "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                    "words": len(notes.split())
                })

                st.session_state.last_activity = f"Created {note_style.lower()}"

                if len(st.session_state.pdf_text) > 26000:
                    st.info("Large PDF: the first 26,000 characters were sent for processing. Some later content may not be covered.")

                st.success("Your notes are ready!")

    if st.session_state.last_notes:
        st.markdown('<div class="section-title">Your study notes</div>', unsafe_allow_html=True)
        st.markdown(st.session_state.last_notes)

        c1, c2 = st.columns(2)

        with c1:
            st.download_button(
                "⬇️ Download TXT",
                data=st.session_state.last_notes,
                file_name="study_buddy_ai_notes.txt",
                mime="text/plain",
                use_container_width=True
            )

        with c2:
            try:
                pdf_data = make_pdf(st.session_state.last_notes)

                st.download_button(
                    "📄 Download PDF",
                    data=pdf_data,
                    file_name="study_buddy_ai_notes.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"PDF export error: {e}")


elif st.session_state.page == "Study Chat":

    show_heading("Study Chat", "Your personal AI tutor for doubts, concepts and explanations.")

    st.markdown("""
    <div class="panel">
      <div class="panel-title">💬 Meet your AI tutor</div>
      <div class="panel-subtitle">Ask a question and get a clear, student-friendly explanation.</div>
      <span class="status-chip">✦ POWERED BY GROQ AI</span>
    </div>
    """, unsafe_allow_html=True)

    if st.button("＋ Start new chat", key="new_chat"):
        st.session_state.chat_messages = []
        st.session_state.last_activity = "Started a new chat"
        st.rerun()

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_prompt = st.chat_input("Ask your study question...")

    if user_prompt:
        st.session_state.chat_messages.append({
            "role": "user",
            "content": user_prompt
        })

        with st.chat_message("user"):
            st.markdown(user_prompt)

        messages = [{
            "role": "system",
            "content": (
                "You are Study Buddy AI, a helpful academic tutor. "
                "Explain concepts in simple, clear language. "
                "Use examples, headings, formulas and steps when useful. "
                "When asked for programming, provide complete working code. "
                "Be accurate and admit uncertainty when necessary."
            )
        }]

        messages.extend(st.session_state.chat_messages[-11:])

        client = get_client()
        answer = None

        if client:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        response = client.chat.completions.create(
                            model=MODEL,
                            messages=messages,
                            max_tokens=3000,
                            temperature=0.4
                        )
                        answer = response.choices[0].message.content

                    except Exception as e:
                        st.error(f"Chat response error: {e}")

                if answer:
                    st.markdown(answer)

        if answer:
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": answer
            })
            st.session_state.last_activity = "Used Study Chat"
            st.rerun()
        else:
            if st.session_state.chat_messages and st.session_state.chat_messages[-1]["role"] == "user":
                st.session_state.chat_messages.pop()
            st.warning("Message send nahi ho paya. Dobara try karo.")


elif st.session_state.page == "Performance":

    show_heading("Your Performance", "Review the learning activities completed in this session.")

    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card("🧠", st.session_state.generated_quizzes, "Quizzes created")

    with c2:
        metric_card("📚", st.session_state.notes_created, "Notes created")

    with c3:
        metric_card("💬", len(st.session_state.chat_messages), "Chat messages")

    st.markdown('<div class="section-title">Quiz history</div>', unsafe_allow_html=True)

    if st.session_state.quiz_history:
        for item in st.session_state.quiz_history:
            status_text = "Completed" if item["complete"] else "Partial"

            st.markdown(f"""
            <div class="panel">
              <div style="font-size:16px;font-weight:800;color:#17233c">{escape(item['topic'])}</div>
              <div style="color:#75819a;font-size:12px;margin-top:8px">
                {item['questions_requested']} questions requested ·
                {escape(item['difficulty'])} ·
                {item['batches_generated']} batches ·
                {escape(item['date'])}
              </div>
              <div style="margin-top:12px"><span class="status-chip">{status_text}</span></div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Quiz history abhi empty hai. AI Quiz se apna pehla quiz banao.")

    st.markdown('<div class="section-title">Notes history</div>', unsafe_allow_html=True)

    if st.session_state.notes_history:
        for item in st.session_state.notes_history:
            st.markdown(f"""
            <div class="panel">
              <div style="font-size:16px;font-weight:800;color:#17233c">{escape(item['style'])}</div>
              <div style="color:#75819a;font-size:12px;margin-top:8px">
                {item['words']} words · {escape(item['date'])}
              </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Notes history abhi empty hai. PDF Notes se notes generate karo.")

    st.caption("Performance data is stored in the active session and may reset when the session restarts.")


elif st.session_state.page == "Settings":

    show_heading("Settings", "Your workspace information and data management.")

    st.markdown("""
    <div class="panel">
      <div class="panel-title">🎨 Your workspace</div>
      <div class="panel-subtitle">A clean green-and-white design made for focused learning.</div>
      <span class="status-chip">STUDY BUDDY AI</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="panel">
      <div class="panel-title">🤖 AI configuration</div>
      <div class="panel-subtitle">The app uses Groq API for quiz generation, notes and chat.</div>
      <div style="font-weight:700;color:#17233c">Model</div>
      <code>openai/gpt-oss-20b</code>
      <div style="height:12px"></div>
      <div style="font-weight:700;color:#17233c">API key</div>
      <div style="color:#75819a;font-size:13px">Stored in Streamlit Secrets and not displayed here.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Manage your data</div>', unsafe_allow_html=True)
    st.warning("Clearing history removes the selected session data. This action cannot be undone.")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("🗑️ Clear quiz and notes history", use_container_width=True):
            st.session_state.quiz_history = []
            st.session_state.notes_history = []
            st.session_state.generated_quizzes = 0
            st.session_state.notes_created = 0
            st.session_state.last_quiz = ""
            st.session_state.last_notes = ""
            st.session_state.quiz_partial = False
            st.session_state.last_activity = "Quiz and notes history cleared"
            st.rerun()

    with c2:
        if st.button("🧹 Clear chat history", use_container_width=True):
            st.session_state.chat_messages = []
            st.session_state.last_activity = "Chat history cleared"
            st.rerun()

    st.markdown('<div class="section-title">About your app</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="panel">
      <div style="font-size:22px;font-weight:800;color:#104c46">Study Buddy AI 🎓</div>
      <div style="color:#75819a;font-size:13px;line-height:1.8;margin-top:9px">
        Your personal AI learning workspace for quiz generation,
        PDF notes, study chat and session-based performance tracking.
      </div>
      <div style="margin-top:13px;font-size:12px;font-weight:700;color:#087f5b">
        LEARN SMARTER · GROW FASTER
      </div>
    </div>
    """, unsafe_allow_html=True)


st.markdown("""
<div class="footer">
  STUDY BUDDY AI &nbsp; · &nbsp; LEARN ✦ GROW ✦ ACHIEVE
</div>
""", unsafe_allow_html=True)
