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

PAGES = [
    "Dashboard",
    "AI Quiz",
    "PDF Notes",
    "Study Chat",
    "Performance",
    "Settings"
]

ICONS = {
    "Dashboard": "◈",
    "AI Quiz": "✳",
    "PDF Notes": "▤",
    "Study Chat": "◉",
    "Performance": "↗",
    "Settings": "⚙"
}

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "menu_open" not in st.session_state:
    st.session_state.menu_open = True

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

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

if "last_activity" not in st.session_state:
    st.session_state.last_activity = "Your journey starts here"

if "quiz_topic" not in st.session_state:
    st.session_state.quiz_topic = ""

if "quiz_partial" not in st.session_state:
    st.session_state.quiz_partial = False

if "notes_title" not in st.session_state:
    st.session_state.notes_title = ""

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --paper: #F7F8F4;
    --white: #FFFFFF;
    --ink: #172E25;
    --muted: #77867D;
    --green: #087F5B;
    --green-dark: #075C43;
    --mint: #DDF3E5;
    --line: #E1E8E0;
    --lime: #B9E8A5;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: var(--paper);
    color: var(--ink);
}

header[data-testid="stHeader"] {
    background: transparent;
}

#MainMenu, footer {
    visibility: hidden;
}

.block-container {
    max-width: 1500px;
    padding-top: 1.1rem;
    padding-bottom: 4rem;
    padding-left: 3.4rem;
    padding-right: 3.4rem;
}

[data-testid="stSidebar"] {
    background: #FFFFFF;
}

[data-testid="stVerticalBlock"] {
    gap: 0.85rem;
}

h1, h2, h3, h4 {
    font-family: 'Manrope', sans-serif !important;
    color: var(--ink);
    letter-spacing: -0.055em;
}

p, li {
    line-height: 1.7;
}

div.stButton > button {
    border-radius: 12px;
    min-height: 43px;
    font-weight: 600;
    border: 1px solid var(--line);
    background: white;
    color: var(--ink);
    transition: all 0.18s ease;
}

div.stButton > button:hover {
    border-color: var(--green);
    color: var(--green);
    background: #F0F8F2;
}

div.stButton > button[kind="primary"] {
    background: var(--green);
    color: white;
    border: 1px solid var(--green);
}

div.stButton > button[kind="primary"]:hover {
    background: var(--green-dark);
    color: white;
}

.stTextInput input, .stTextArea textarea,
.stSelectbox div[data-baseweb="select"],
.stNumberInput input {
    border-radius: 12px !important;
}

[data-testid="stFileUploader"] {
    background: #FFFFFF;
    border: 1px dashed #9FC8AB;
    border-radius: 18px;
    padding: 12px;
}

hr {
    border-color: var(--line);
}

.sb-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    padding: 8px 0 23px 0;
    border-bottom: 1px solid var(--line);
    margin-bottom: 26px;
}

.sb-brand {
    display: flex;
    align-items: center;
    gap: 12px;
}

.sb-logo {
    width: 43px;
    height: 43px;
    display: flex;
    justify-content: center;
    align-items: center;
    background: var(--green);
    color: white;
    border-radius: 14px 14px 14px 4px;
    font-family: 'Manrope', sans-serif;
    font-size: 20px;
    font-weight: 800;
}

.sb-brand-name {
    font-family: 'Manrope', sans-serif;
    font-size: 17px;
    font-weight: 800;
    letter-spacing: -0.7px;
    color: var(--ink);
}

.sb-brand-sub {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    color: var(--muted);
    letter-spacing: 1.5px;
    margin-top: 3px;
}

.sb-top-right {
    display: flex;
    align-items: center;
    gap: 9px;
    color: var(--muted);
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.5px;
}

.sb-status-dot {
    display: inline-block;
    width: 7px;
    height: 7px;
    background: #24A36B;
    border-radius: 50%;
    margin-right: 6px;
}

.sb-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 2px;
    color: var(--green);
    font-weight: 500;
    text-transform: uppercase;
}

.sb-title {
    font-family: 'Manrope', sans-serif;
    font-size: clamp(37px, 5.4vw, 70px);
    font-weight: 800;
    line-height: 0.99;
    letter-spacing: -5px;
    color: var(--ink);
    margin: 15px 0 17px 0;
}

.sb-title em {
    color: var(--green);
    font-style: normal;
}

.sb-description {
    color: var(--muted);
    max-width: 500px;
    font-size: 14px;
    line-height: 1.9;
}

.sb-hero {
    background: #FFFFFF;
    border: 1px solid var(--line);
    border-radius: 24px;
    padding: 35px;
    position: relative;
    overflow: hidden;
    min-height: 330px;
}

.sb-hero::before {
    content: "";
    position: absolute;
    width: 300px;
    height: 300px;
    right: -100px;
    top: -140px;
    border: 1px solid #D9EBDD;
    border-radius: 50%;
}

.sb-hero::after {
    content: "";
    position: absolute;
    width: 220px;
    height: 220px;
    right: -57px;
    top: -100px;
    border: 1px solid #BFDCC7;
    border-radius: 50%;
}

.sb-hero-art {
    height: 245px;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
}

.sb-orbit {
    width: 205px;
    height: 205px;
    border: 1px solid #C9E2D0;
    border-radius: 50%;
    position: absolute;
    display: flex;
    align-items: center;
    justify-content: center;
}

.sb-orbit-inner {
    width: 145px;
    height: 145px;
    border: 1px dashed #A7CFB3;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #F3FAF3;
}

.sb-orbit-core {
    width: 83px;
    height: 83px;
    background: var(--green);
    color: white;
    border-radius: 27px 27px 27px 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 30px;
    font-weight: 700;
    box-shadow: 0 15px 35px #087F5B2B;
    transform: rotate(-7deg);
}

.sb-orbit-core span {
    transform: rotate(7deg);
}

.sb-float {
    position: absolute;
    background: white;
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 10px 13px;
    font-size: 10px;
    font-family: 'DM Mono', monospace;
    box-shadow: 0 8px 25px #173D2510;
    color: var(--green-dark);
}

.sb-float-a { top: 16px; right: 1px; }
.sb-float-b { bottom: 22px; left: 0; }
.sb-float-c { bottom: 9px; right: 0; }

.sb-section-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin: 33px 0 15px 0;
}

.sb-section-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 1.8px;
    color: var(--muted);
    text-transform: uppercase;
}

.sb-section-title {
    font-family: 'Manrope', sans-serif;
    font-size: 24px;
    letter-spacing: -1.2px;
    font-weight: 800;
    margin-top: 4px;
    color: var(--ink);
}

.sb-feature {
    min-height: 220px;
    height: 100%;
    border: 1px solid var(--line);
    border-radius: 20px;
    padding: 22px;
    background: #FFFFFF;
    position: relative;
    overflow: hidden;
    transition: transform .2s ease, border-color .2s ease;
}

.sb-feature:hover {
    transform: translateY(-3px);
    border-color: #A8D2B3;
}

.sb-feature-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 26px;
}

.sb-feature-icon {
    width: 42px;
    height: 42px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #E7F5E9;
    color: var(--green);
    font-size: 21px;
}

.sb-index {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: #9AA79D;
}

.sb-feature h3 {
    font-size: 20px;
    font-weight: 800;
    letter-spacing: -1px;
    margin: 0 0 7px 0;
}

.sb-feature p {
    color: var(--muted);
    font-size: 12px;
    line-height: 1.7;
    margin: 0;
}

.sb-feature-link {
    margin-top: 17px;
    color: var(--green);
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: .4px;
}

.sb-metric {
    border-top: 2px solid var(--green);
    padding: 17px 0 13px 0;
}

.sb-metric-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 1px;
    color: var(--muted);
    text-transform: uppercase;
}

.sb-metric-value {
    font-family: 'Manrope', sans-serif;
    font-size: 36px;
    letter-spacing: -2px;
    font-weight: 800;
    margin-top: 8px;
    color: var(--ink);
}

.sb-metric-note {
    color: var(--green);
    font-size: 11px;
    margin-top: 3px;
}

.sb-quote {
    background: #E7F4E9;
    border-radius: 20px;
    padding: 23px;
    color: var(--green-dark);
    position: relative;
    overflow: hidden;
}

.sb-quote-mark {
    font-family: 'Manrope', sans-serif;
    font-size: 40px;
    line-height: 1;
    color: #78B88C;
}

.sb-quote-text {
    font-family: 'Manrope', sans-serif;
    font-size: 19px;
    font-weight: 700;
    line-height: 1.5;
    letter-spacing: -.5px;
}

.sb-quote-caption {
    margin-top: 10px;
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    letter-spacing: 1px;
    color: #4F8762;
}

.sb-page-head {
    border-bottom: 1px solid var(--line);
    padding: 8px 0 23px 0;
    margin-bottom: 26px;
}

.sb-page-title {
    font-family: 'Manrope', sans-serif;
    font-size: clamp(34px, 4vw, 52px);
    letter-spacing: -3px;
    font-weight: 800;
    line-height: 1.1;
    margin: 10px 0;
}

.sb-page-description {
    color: var(--muted);
    font-size: 13px;
    line-height: 1.8;
    max-width: 650px;
}

.sb-panel {
    background: white;
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 23px;
}

.sb-panel-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 1.5px;
    color: var(--green);
    text-transform: uppercase;
}

.sb-panel-title {
    font-family: 'Manrope', sans-serif;
    font-weight: 800;
    font-size: 21px;
    letter-spacing: -1px;
    margin: 7px 0 12px 0;
}

.sb-mini-label {
    font-family: 'DM Mono', monospace;
    color: var(--muted);
    font-size: 10px;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.sb-nav-title {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: #8C9A90;
    letter-spacing: 2px;
    margin: 5px 0 12px 0;
}

.sb-nav-caption {
    color: var(--muted);
    font-size: 12px;
    line-height: 1.7;
    margin: 14px 0 20px 0;
}

.sb-footer {
    border-top: 1px solid var(--line);
    margin-top: 38px;
    padding-top: 17px;
    display: flex;
    justify-content: space-between;
    gap: 10px;
    color: #89978E;
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    letter-spacing: 1px;
}

[data-testid="stMetric"] {
    background: white;
    padding: 18px;
    border: 1px solid var(--line);
    border-radius: 16px;
}

[data-testid="stMetricLabel"] {
    color: var(--muted);
}

[data-testid="stMetricValue"] {
    color: var(--green-dark);
    font-family: 'Manrope', sans-serif;
}

[data-testid="stChatMessage"] {
    border: 1px solid var(--line);
    border-radius: 15px;
    padding: 13px;
    background: white;
}

[data-testid="stProgressBar"] > div > div {
    background: var(--green);
}

.stAlert {
    border-radius: 13px;
}

@media (max-width: 800px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        padding-top: .7rem;
    }

    .sb-title {
        letter-spacing: -2.5px;
        font-size: 43px;
    }

    .sb-hero {
        padding: 23px;
    }

    .sb-hero-art {
        height: 215px;
    }

    .sb-orbit {
        width: 175px;
        height: 175px;
    }

    .sb-orbit-inner {
        width: 125px;
        height: 125px;
    }

    .sb-orbit-core {
        width: 72px;
        height: 72px;
    }

    .sb-top-right {
        font-size: 8px;
    }

    .sb-feature {
        min-height: 195px;
        padding: 17px;
    }

    .sb-footer {
        flex-direction: column;
    }
}
</style>
""", unsafe_allow_html=True)


def get_client():
    try:
        api_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        api_key = ""

    if not api_key:
        return None

    try:
        return Groq(api_key=api_key)
    except Exception:
        return None


def ask_ai(prompt, max_tokens=3000, temperature=0.4):
    client = get_client()

    if client is None:
        st.error(
            "Groq API key nahi mili. Streamlit Cloud ke "
            "App Settings → Secrets mein GROQ_API_KEY set karo."
        )
        return None

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()

    except Exception as error:
        st.error(f"AI request complete nahi hui: {error}")
        return None


def page_header(number, title, description, tag="STUDY BUDDY AI"):
    st.markdown(f"""
    <div class="sb-page-head">
        <div class="sb-eyebrow">{escape(tag)} / {escape(number)}</div>
        <div class="sb-page-title">{title}</div>
        <div class="sb-page-description">{escape(description)}</div>
    </div>
    """, unsafe_allow_html=True)


def section_head(label, title):
    st.markdown(f"""
    <div class="sb-section-head">
        <div>
            <div class="sb-section-label">{escape(label)}</div>
            <div class="sb-section-title">{escape(title)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def feature_card(index, icon, title, description, action):
    st.markdown(f"""
    <div class="sb-feature">
        <div class="sb-feature-top">
            <div class="sb-feature-icon">{icon}</div>
            <div class="sb-index">{index}</div>
        </div>
        <h3>{escape(title)}</h3>
        <p>{escape(description)}</p>
        <div class="sb-feature-link">OPEN WORKSPACE ↗</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button(
        f"Explore {title} ↗",
        key=f"feature_{index}",
        use_container_width=True
    ):
        st.session_state.page = action
        st.rerun()


def metric_card(label, value, note):
    st.markdown(f"""
    <div class="sb-metric">
        <div class="sb-metric-label">{escape(label)}</div>
        <div class="sb-metric-value">{escape(str(value))}</div>
        <div class="sb-metric-note">{escape(note)}</div>
    </div>
    """, unsafe_allow_html=True)


def make_pdf(text_content, title="Study Notes"):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=48,
        leftMargin=48,
        topMargin=48,
        bottomMargin=48
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        textColor=colors.HexColor("#087F5B"),
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=28,
        spaceAfter=18
    )

    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=16,
        spaceAfter=8,
        textColor=colors.HexColor("#24392E")
    )

    story = [
        Paragraph(escape(title), title_style),
        Paragraph(
            f"Generated by Study Buddy AI · {datetime.now().strftime('%d %b %Y')}",
            styles["Normal"]
        ),
        Spacer(1, 18)
    ]

    for line in text_content.splitlines():
        line = line.strip()

        if not line:
            story.append(Spacer(1, 6))
            continue

        safe_line = escape(line)

        if line.startswith("#"):
            clean_heading = line.lstrip("#").strip()
            story.append(Paragraph(escape(clean_heading), styles["Heading2"]))

        elif line.startswith(("- ", "• ", "* ")):
            clean_bullet = line[2:].strip()
            story.append(
                Paragraph("&#8226; " + escape(clean_bullet), body_style)
            )

        else:
            story.append(Paragraph(safe_line, body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def render_topbar():
    left, right = st.columns([3, 1])

    with left:
        menu_col, brand_col = st.columns([0.38, 5])

        with menu_col:
            if st.button(
                "☰",
                key="hamburger",
                help="Open or close navigation",
                use_container_width=True
            ):
                st.session_state.menu_open = not st.session_state.menu_open
                st.rerun()

        with brand_col:
            st.markdown("""
            <div class="sb-brand">
                <div class="sb-logo">S.</div>
                <div>
                    <div class="sb-brand-name">Study Buddy AI</div>
                    <div class="sb-brand-sub">YOUR PERSONAL LEARNING SPACE</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with right:
        st.markdown("""
        <div style="text-align:right;padding-top:10px">
            <span class="sb-status-dot"></span>
            <span style="font-family:'DM Mono',monospace;font-size:10px;
            color:#718178;letter-spacing:1px">WORKSPACE READY</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(
        '<div style="height:1px;background:#E1E8E0;margin:18px 0 24px 0"></div>',
        unsafe_allow_html=True
    )


def render_navigation():
    if not st.session_state.menu_open:
        return

    with st.container(border=True):
        st.markdown(
            '<div class="sb-nav-title">☰ &nbsp; YOUR WORKSPACE</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="sb-nav-caption">Everything you need to learn, '
            'practice and keep moving forward.</div>',
            unsafe_allow_html=True
        )

        cols = st.columns(3)

        for index, page in enumerate(PAGES):
            with cols[index % 3]:
                is_current = st.session_state.page == page

                if st.button(
                    f"{ICONS[page]}   {page}"
                    + ("  •" if is_current else ""),
                    key=f"nav_{page}",
                    type="primary" if is_current else "secondary",
                    use_container_width=True
                ):
                    st.session_state.page = page
                    st.rerun()

        st.markdown(
            '<div style="height:5px"></div>',
            unsafe_allow_html=True
        )


def dashboard():
    st.markdown("""
    <div class="sb-hero">
        <div class="sb-eyebrow">A BETTER WAY TO LEARN &nbsp; / &nbsp; 001</div>
        <div class="sb-title">Think deeper.<br><em>Learn different.</em></div>
        <div class="sb-description">
            Your ideas deserve more than ordinary notes.
            Explore concepts, challenge your understanding and
            turn study time into real progress.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height:18px"></div>', unsafe_allow_html=True)

    art_col, quote_col = st.columns([1.1, 1])

    with art_col:
        st.markdown("""
        <div class="sb-panel" style="min-height:290px">
            <div class="sb-panel-label">YOUR LEARNING UNIVERSE</div>
            <div class="sb-hero-art">
                <div class="sb-orbit">
                    <div class="sb-orbit-inner">
                        <div class="sb-orbit-core"><span>S.</span></div>
                    </div>
                </div>
                <div class="sb-float sb-float-a">IDEAS / 01</div>
                <div class="sb-float sb-float-b">LEARN ↗ GROW</div>
                <div class="sb-float sb-float-c">STAY CURIOUS</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with quote_col:
        st.markdown("""
        <div class="sb-quote" style="min-height:290px">
            <div class="sb-quote-mark">“</div>
            <div class="sb-quote-text">
                Small steps every day lead to extraordinary understanding.
            </div>
            <div class="sb-quote-caption">A REMINDER FOR YOUR NEXT CHAPTER</div>
            <div style="height:35px"></div>
            <div style="border-top:1px solid #BFDCC7;padding-top:14px;
            font-family:'DM Mono',monospace;font-size:10px;letter-spacing:1px">
                YOUR SPACE. YOUR PACE. YOUR PROGRESS.
            </div>
        </div>
        """, unsafe_allow_html=True)

    section_head("THE TOOLKIT", "Choose your next move")

    c1, c2 = st.columns(2)

    with c1:
        feature_card(
            "01", "✳", "AI Quiz Lab",
            "Generate practice questions by topic, difficulty and format.",
            "AI Quiz"
        )

    with c2:
        feature_card(
            "02", "▤", "Notes Studio",
            "Transform PDF study material into clear, organised notes.",
            "PDF Notes"
        )

    c3, c4 = st.columns(2)

    with c3:
        feature_card(
            "03", "◉", "Study Chat",
            "Ask questions and work through concepts with your AI tutor.",
            "Study Chat"
        )

    with c4:
        feature_card(
            "04", "↗", "Growth Tracker",
            "Review your activity and see what you have created so far.",
            "Performance"
        )

    section_head("YOUR ACTIVITY", "A little progress adds up")

    m1, m2, m3 = st.columns(3)

    with m1:
        metric_card(
            "QUIZ SESSIONS",
            st.session_state.generated_quizzes,
            "Practice sets generated"
        )

    with m2:
        metric_card(
            "NOTES CREATED",
            st.session_state.notes_created,
            "Study resources prepared"
        )

    with m3:
        metric_card(
            "CHAT MESSAGES",
            sum(
                1 for message in st.session_state.chat_messages
                if message["role"] == "user"
            ),
            "Questions asked"
        )

    st.markdown("""
    <div class="sb-footer">
        <span>STUDY BUDDY AI</span>
        <span>MADE FOR CURIOUS MINDS</span>
    </div>
    """, unsafe_allow_html=True)


def ai_quiz():
    page_header(
        "01 / PRACTICE",
        "AI Quiz Lab.",
        "Build a practice set around what you are learning. "
        "Choose a topic and let AI prepare the questions."
    )

    left, right = st.columns([1.05, 0.95])

    with left:
        st.markdown("""
        <div class="sb-panel">
            <div class="sb-panel-label">01 / CONFIGURE</div>
            <div class="sb-panel-title">Design your practice</div>
        </div>
        """, unsafe_allow_html=True)

        topic = st.text_input(
            "Topic or subject",
            placeholder="e.g. BJT, recursion, electrochemistry",
            key="quiz_topic_input"
        )

        level = st.selectbox(
            "Difficulty",
            ["Easy", "Medium", "Hard", "Mixed"]
        )

        question_type = st.selectbox(
            "Question format",
            ["MCQ", "Short Answer", "Mixed"]
        )

        language = st.selectbox(
            "Answer language",
            ["Simple English", "Hindi", "Hinglish"]
        )

        question_count = st.select_slider(
            "Number of questions",
            options=[5, 10, 15, 20, 30, 40, 50],
            value=10
        )

        generate = st.button(
            "✳  Generate my quiz",
            type="primary",
            use_container_width=True
        )

    with right:
        st.markdown("""
        <div class="sb-quote" style="min-height:250px">
            <div class="sb-quote-mark">✳</div>
            <div class="sb-quote-text">Understanding gets stronger when you test it.</div>
            <div class="sb-quote-caption">PRACTICE MODE / ON</div>
            <div style="height:26px"></div>
            <div style="border-top:1px solid #BFDCC7;padding-top:15px">
                <div style="font-family:'DM Mono',monospace;font-size:10px;
                letter-spacing:1px">YOUR SETTINGS</div>
                <div style="font-size:13px;margin-top:8px;line-height:1.8">
                    Topic-focused questions<br>
                    Adjustable difficulty<br>
                    Downloadable practice material
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="sb-panel">
            <div class="sb-panel-label">STUDY TIP</div>
            <div style="font-size:13px;line-height:1.8;margin-top:8px">
                Try answering questions on your own before checking the
                explanations. This makes revision more meaningful.
            </div>
        </div>
        """, unsafe_allow_html=True)

    if generate:
        if not topic.strip():
            st.warning("Pehle apna topic enter karo.")
        else:
            with st.spinner("Preparing your practice questions..."):
                batches = []
                remaining = question_count
                question_number = 1
                failed = False

                while remaining > 0:
                    batch_size = min(10, remaining)

                    prompt = f"""
You are a helpful college study tutor.

Create exactly {batch_size} numbered questions for this topic:
{topic}

Difficulty: {level}
Question format: {question_type}
Language: {language}

Start numbering from {question_number}.

For MCQ questions:
- Provide four options A, B, C, D.
- Mark the correct answer.
- Explain the answer in simple language.

For short answer questions:
- Provide a clear model answer.
- Include an explanation where helpful.

For mixed format, use a mix of MCQs and short-answer questions.

Use accurate educational information.
Keep formatting clear and readable.
Do not include an introductory paragraph.
Do not skip question numbers.
"""

                    result = ask_ai(prompt, max_tokens=4500)

                    if not result:
                        failed = True
                        break

                    batches.append(result)
                    remaining -= batch_size
                    question_number += batch_size

                if batches:
                    quiz_text = "\n\n".join(batches)

                    st.session_state.last_quiz = quiz_text
                    st.session_state.quiz_topic = topic
                    st.session_state.generated_quizzes += 1
                    st.session_state.quiz_partial = failed

                    st.session_state.quiz_history.append({
                        "topic": topic,
                        "count": question_count,
                        "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                        "content": quiz_text
                    })

                    st.session_state.last_activity = (
                        f"Generated a quiz on {topic}"
                    )

                    if failed:
                        st.warning(
                            "Quiz partially generated. Neeche available "
                            "questions dekh sakte ho."
                        )
                    else:
                        st.success("Your quiz is ready!")

    if st.session_state.last_quiz:
        section_head("YOUR GENERATED SET", st.session_state.quiz_topic)

        st.markdown(
            '<div class="sb-panel-label">PRACTICE MATERIAL / GENERATED BY AI</div>',
            unsafe_allow_html=True
        )

        st.markdown(st.session_state.last_quiz)

        st.download_button(
            "Download quiz as TXT",
            data=st.session_state.last_quiz,
            file_name="study_buddy_quiz.txt",
            mime="text/plain",
            use_container_width=True
        )


def pdf_notes():
    page_header(
        "02 / ORGANISE",
        "Notes Studio.",
        "Upload a PDF and turn its content into structured revision notes."
    )

    st.markdown("""
    <div class="sb-panel">
        <div class="sb-panel-label">DOCUMENT WORKSPACE</div>
        <div class="sb-panel-title">Bring your study material</div>
        <div style="color:#77867D;font-size:13px;line-height:1.8">
            Upload a text-based PDF, select your preferred style and
            create notes that are easier to revise.
        </div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload your PDF",
        type=["pdf"],
        key="notes_pdf_upload"
    )

    style = st.selectbox(
        "Notes style",
        [
            "Detailed notes with headings",
            "Exam revision notes",
            "Short summary",
            "Question and answer format",
            "Bullet-point notes"
        ]
    )

    language = st.selectbox(
        "Notes language",
        ["Simple English", "Hindi", "Hinglish"],
        key="notes_language"
    )

    if uploaded_file:
        try:
            reader = PdfReader(uploaded_file)
            pages = []
            for page in reader.pages:
                pages.append(page.extract_text() or "")

            extracted_text = "\n".join(pages).strip()

            if extracted_text:
                st.session_state.pdf_text = extracted_text
                st.info(
                    f"PDF ready: {len(reader.pages)} pages detected."
                )
            else:
                st.warning(
                    "Is PDF se selectable text nahi mila. "
                    "Scanned PDF ke liye OCR ki zaroorat ho sakti hai."
                )

        except Exception as error:
            st.error(f"PDF read nahi ho saki: {error}")

    create_notes = st.button(
        "▤  Create study notes",
        type="primary",
        use_container_width=True
    )

    if create_notes:
        if not st.session_state.pdf_text:
            st.warning("Pehle ek readable PDF upload karo.")
        else:
            with st.spinner("Reading and organising your material..."):
                source_text = st.session_state.pdf_text[:26000]

                prompt = f"""
You are an expert educational note-making assistant.

Create useful study notes from the provided material.

Style: {style}
Language: {language}

Requirements:
- Use clear headings and subheadings.
- Explain important concepts accurately.
- Preserve key definitions, formulas, examples and facts.
- Use bullet points where suitable.
- Make the notes easy for a college student to revise.
- Do not invent information that is not supported by the material.
- If a formula is present, explain its symbols when possible.
- Do not claim that you covered content you did not receive.

SOURCE MATERIAL:
{source_text}
"""

                notes = ask_ai(prompt, max_tokens=6000)

                if notes:
                    st.session_state.last_notes = notes
                    st.session_state.notes_title = uploaded_file.name
                    st.session_state.notes_created += 1

                    st.session_state.notes_history.append({
                        "title": uploaded_file.name,
                        "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                        "content": notes
                    })

                    st.session_state.last_activity = (
                        f"Created notes from {uploaded_file.name}"
                    )

                    st.success("Your notes are ready!")

    if st.session_state.last_notes:
        section_head("YOUR NOTES", "Ready for revision")

        st.markdown(st.session_state.last_notes)

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                "Download TXT",
                data=st.session_state.last_notes,
                file_name="study_buddy_notes.txt",
                mime="text/plain",
                use_container_width=True
            )

        with col2:
            try:
                pdf_bytes = make_pdf(
                    st.session_state.last_notes,
                    "Study Buddy AI Notes"
                )

                st.download_button(
                    "Download PDF",
                    data=pdf_bytes,
                    file_name="study_buddy_notes.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            except Exception as error:
                st.error(f"PDF create nahi ho saki: {error}")


def study_chat():
    page_header(
        "03 / EXPLORE",
        "Study Chat.",
        "A study space for questions, explanations and step-by-step learning."
    )

    left, right = st.columns([1.7, 0.8])

    with left:
        st.markdown("""
        <div class="sb-panel">
            <div class="sb-panel-label">YOUR AI STUDY PARTNER</div>
            <div class="sb-panel-title">What are you learning today?</div>
            <div style="color:#77867D;font-size:13px;line-height:1.8">
                Ask a question, request an example or ask for a difficult
                topic to be explained in simpler words.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown("""
        <div class="sb-quote">
            <div class="sb-panel-label">QUICK REMINDER</div>
            <div class="sb-quote-text" style="font-size:17px;margin-top:13px">
                There are no silly questions when you are learning.
            </div>
        </div>
        """, unsafe_allow_html=True)

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_prompt = st.chat_input(
        "Ask your study question..."
    )

    if user_prompt:
        st.session_state.chat_messages.append({
            "role": "user",
            "content": user_prompt
        })

        with st.chat_message("user"):
            st.markdown(user_prompt)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are Study Buddy AI, a patient and accurate study tutor. "
                    "Explain concepts clearly, use simple language when useful, "
                    "show steps for calculations, and do not invent facts. "
                    "Adapt to the student's language."
                )
            }
        ]

        messages.extend(st.session_state.chat_messages[-12:])

        client = get_client()

        if client is None:
            st.error(
                "Groq API key nahi mili. Streamlit Cloud ke "
                "App Settings → Secrets mein GROQ_API_KEY set karo."
            )
        else:
            try:
                with st.chat_message("assistant"):
                    with st.spinner("Thinking through your question..."):
                        response = client.chat.completions.create(
                            model=MODEL,
                            messages=messages,
                            temperature=0.4,
                            max_tokens=3000
                        )

                        answer = response.choices[0].message.content.strip()

                    st.markdown(answer)

                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": answer
                })

                st.session_state.last_activity = "Studied with AI Chat"

            except Exception as error:
                st.error(f"Chat response nahi aa saka: {error}")

    if st.session_state.chat_messages:
        if st.button("Clear chat history", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()


def performance():
    page_header(
        "04 / REFLECT",
        "Your progress.",
        "A simple overview of the learning work you have completed in this session."
    )

    a, b, c = st.columns(3)

    with a:
        st.metric(
            "Quiz sessions",
            st.session_state.generated_quizzes
        )

    with b:
        st.metric(
            "Notes created",
            st.session_state.notes_created
        )

    with c:
        st.metric(
            "Questions asked",
            sum(
                1 for message in st.session_state.chat_messages
                if message["role"] == "user"
            )
        )

    section_head("RECENT WORK", "Your learning activity")

    st.markdown(f"""
    <div class="sb-panel">
        <div class="sb-panel-label">LATEST ACTIVITY</div>
        <div class="sb-panel-title">{escape(st.session_state.last_activity)}</div>
        <div style="color:#77867D;font-size:12px">
            This activity summary is stored in your current app session.
        </div>
    </div>
    """, unsafe_allow_html=True)

    section_head("PRACTICE HISTORY", "Generated quizzes")

    if st.session_state.quiz_history:
        for item in reversed(st.session_state.quiz_history[-10:]):
            with st.expander(
                f"{item['topic']} · {item['count']} questions · {item['date']}"
            ):
                st.markdown(item["content"])

                st.download_button(
                    "Download this quiz",
                    data=item["content"],
                    file_name="study_buddy_quiz.txt",
                    mime="text/plain",
                    key="download_quiz_" + str(
                        st.session_state.quiz_history.index(item)
                    )
                )
    else:
        st.info("Your generated quizzes will appear here.")

    section_head("NOTES HISTORY", "Your study resources")

    if st.session_state.notes_history:
        for index, item in enumerate(reversed(st.session_state.notes_history[-10:])):
            with st.expander(f"{item['title']} · {item['date']}"):
                st.markdown(item["content"])

                st.download_button(
                    "Download these notes",
                    data=item["content"],
                    file_name="study_buddy_notes.txt",
                    mime="text/plain",
                    key=f"download_notes_{index}"
                )
    else:
        st.info("Your created notes will appear here.")

    st.markdown("""
    <div class="sb-footer">
        <span>PROGRESS IS BUILT ONE SESSION AT A TIME</span>
        <span>STUDY BUDDY AI</span>
    </div>
    """, unsafe_allow_html=True)


def settings():
    page_header(
        "05 / PREFERENCES",
        "Your workspace.",
        "Manage your current session and view app configuration."
    )

    st.markdown("""
    <div class="sb-panel">
        <div class="sb-panel-label">PRODUCT IDENTITY</div>
        <div class="sb-panel-title">Study Buddy AI</div>
        <div style="color:#77867D;font-size:13px;line-height:1.9">
            A personal learning assistant for practice quizzes,
            PDF notes and study conversations.
        </div>
        <div style="margin-top:14px;font-family:'DM Mono',monospace;
        font-size:10px;letter-spacing:1px;color:#087F5B">
            MODEL CONFIGURATION / GROQ
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="sb-panel">
        <div class="sb-panel-label">SESSION INFORMATION</div>
        <div class="sb-panel-title">Current activity</div>
        <div style="color:#77867D;font-size:13px;line-height:1.9">
            Your quiz, notes and chat history are stored in the active
            Streamlit session. They may reset when the session restarts.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)

    st.subheader("Reset session data")

    st.warning(
        "This clears your quiz history, generated notes and chat messages "
        "from the current session."
    )

    confirm = st.checkbox(
        "I understand that this will clear my current session history."
    )

    if st.button(
        "Clear session history",
        type="primary",
        use_container_width=True
    ):
        if not confirm:
            st.warning("Please confirm before clearing the history.")
        else:
            st.session_state.chat_messages = []
            st.session_state.quiz_history = []
            st.session_state.notes_history = []
            st.session_state.generated_quizzes = 0
            st.session_state.notes_created = 0
            st.session_state.last_quiz = ""
            st.session_state.last_notes = ""
            st.session_state.pdf_text = ""
            st.session_state.last_activity = "Your journey starts here"
            st.session_state.quiz_topic = ""
            st.session_state.quiz_partial = False
            st.session_state.notes_title = ""

            st.success("Current session history cleared.")
            st.rerun()

    st.markdown("""
    <div class="sb-footer">
        <span>STUDY BUDDY AI</span>
        <span>KEEP LEARNING. KEEP GROWING.</span>
    </div>
    """, unsafe_allow_html=True)


render_topbar()
render_navigation()

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
