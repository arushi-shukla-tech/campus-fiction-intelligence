import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

st.set_page_config(
    page_title="Campus Intelligence",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CUSTOM DESIGN ----------------

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #f5f7fb;
}

section[data-testid="stSidebar"] {
    background: #111827;
    border-right: 1px solid #273244;
}

section[data-testid="stSidebar"] * {
    color: #f3f4f6;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}

.hero {
    padding: 35px;
    border-radius: 24px;
    background: linear-gradient(135deg, #111827, #1e293b);
    color: white;
    margin-bottom: 25px;
    box-shadow: 0 12px 35px rgba(15, 23, 42, 0.18);
}

.hero-small {
    color: #94a3b8;
    font-size: 14px;
    margin-bottom: 8px;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.hero h1 {
    font-size: 42px;
    margin: 0;
    font-weight: 800;
}

.hero p {
    color: #cbd5e1;
    font-size: 16px;
    margin-top: 10px;
}

.metric-card {
    background: white;
    padding: 22px;
    border-radius: 18px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 6px 20px rgba(15, 23, 42, 0.06);
    min-height: 125px;
}

.metric-label {
    color: #64748b;
    font-size: 13px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .6px;
}

.metric-value {
    color: #111827;
    font-size: 28px;
    font-weight: 800;
    margin-top: 8px;
}

.section-title {
    font-size: 22px;
    font-weight: 800;
    color: #111827;
    margin-top: 25px;
    margin-bottom: 15px;
}

.insight-card {
    background: white;
    padding: 24px;
    border-radius: 20px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 7px 25px rgba(15, 23, 42, 0.06);
    height: 100%;
}

.insight-label {
    font-size: 12px;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: .8px;
}

.insight-value {
    font-size: 23px;
    font-weight: 800;
    color: #111827;
    margin-top: 8px;
}

.insight-text {
    color: #64748b;
    font-size: 13px;
    margin-top: 7px;
}

.pulse {
    padding: 24px;
    border-radius: 20px;
    background: linear-gradient(135deg, #ffffff, #f8fafc);
    border: 1px solid #e2e8f0;
    margin: 20px 0;
}

.pulse-title {
    font-size: 13px;
    font-weight: 700;
    color: #64748b;
    letter-spacing: 1px;
}

.pulse-status {
    font-size: 30px;
    font-weight: 800;
    color: #111827;
    margin-top: 5px;
}

.pulse-description {
    color: #64748b;
    margin-top: 5px;
}

.priority-card {
    background: white;
    padding: 20px;
    border-radius: 18px;
    border: 1px solid #e5e7eb;
    margin-bottom: 12px;
    box-shadow: 0 5px 18px rgba(15, 23, 42, 0.05);
}

.hotspot {
    background: white;
    padding: 20px;
    border-radius: 18px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 5px 18px rgba(15, 23, 42, 0.05);
}

.hotspot-title {
    font-weight: 800;
    font-size: 17px;
    color: #111827;
}

.hotspot-number {
    font-size: 26px;
    font-weight: 800;
    color: #111827;
}

.hotspot-small {
    color: #64748b;
    font-size: 13px;
}

.form-box {
    background: white;
    padding: 30px;
    border-radius: 22px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 8px 30px rgba(15, 23, 42, 0.06);
}

.tip-box {
    background: #eef2ff;
    padding: 18px;
    border-radius: 16px;
    border-left: 4px solid #6366f1;
    color: #3730a3;
}

.footer {
    text-align: center;
    color: #94a3b8;
    padding: 25px;
    font-size: 12px;
}

div.stButton > button {
    border-radius: 12px;
    font-weight: 700;
    min-height: 45px;
}

</style>
""", unsafe_allow_html=True)


# ---------------- GOOGLE SHEETS ----------------

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(credentials)
sheet = client.open("Campus Reports").sheet1


# ---------------- DATA ----------------

def load_data():

    records = sheet.get_all_records()

    columns = [
        "Problem",
        "Location",
        "Time",
        "Severity",
        "Description",
        "Date"
    ]

    if not records:
        return pd.DataFrame(columns=columns)

    df = pd.DataFrame(records)

    for col in columns:
        if col not in df.columns:
            df[col] = ""

    df = df[columns]

    df["Severity"] = pd.to_numeric(
        df["Severity"],
        errors="coerce"
    )

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce",
        dayfirst=True
    )

    df = df.dropna(
        subset=["Problem", "Location", "Severity"]
    )

    for col in ["Problem", "Location", "Time", "Description"]:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
        )

    return df


df = load_data()


# ---------------- FUNCTIONS ----------------

def get_priority(score):

    if score >= 16:
        return "🔴 Critical"

    if score >= 11:
        return "🟠 High"

    if score >= 6:
        return "🟡 Medium"

    return "🟢 Low"


def calculate_priority(data):

    if data.empty:
        return pd.DataFrame()

    result = (
        data.groupby("Problem")
        .agg(
            Reports=("Problem", "count"),
            Average_Severity=("Severity", "mean")
        )
    )

    max_reports = result["Reports"].max()

    if max_reports == 0:
        max_reports = 1

    result["Frequency Score"] = (
        result["Reports"] / max_reports
    ) * 10

    result["Severity Score"] = (
        result["Average_Severity"] / 5
    ) * 10

    result["Priority Score"] = (
        result["Frequency Score"] * 0.5
        + result["Severity Score"] * 0.5
    )

    result["Priority"] = (
        result["Priority Score"]
        .apply(get_priority)
    )

    return result.sort_values(
        "Priority Score",
        ascending=False
    )


def campus_pulse(priority_data):

    if priority_data.empty:
        return "🟢 Stable", "Not enough data to determine campus status."

    highest = priority_data["Priority Score"].max()

    if highest >= 16:
        return (
            "🔴 Critical",
            "Several reported issues require immediate attention."
        )

    if highest >= 11:
        return (
            "🟠 Needs Attention",
            "Some reported issues have high combined frequency and severity."
        )

    if highest >= 6:
        return (
            "🟡 Monitor",
            "Reported issues are present and should be monitored."
        )

    return (
        "🟢 Stable",
        "Current reported issues have relatively low priority scores."
    )


def trend_message(data):

    trend = data.dropna(subset=["Date"]).copy()

    if trend.empty:
        return "Add valid report dates to view the reporting trend."

    daily = (
        trend.groupby(
            trend["Date"].dt.date
        )
        .size()
    )

    if len(daily) < 2:
        return "More dated reports are needed to identify a trend."

    if daily.iloc[-1] > daily.iloc[0]:
        return "Reporting activity is currently increasing."

    if daily.iloc[-1] < daily.iloc[0]:
        return "Reporting activity is currently decreasing."

    return "Reporting activity is currently stable."


# ---------------- SIDEBAR ----------------

st.sidebar.markdown(
    """
    <div style="padding:10px 0 20px 0;">
        <div style="font-size:28px;">🎓</div>
        <div style="font-size:20px;font-weight:800;">
            Campus Intelligence
        </div>
        <div style="font-size:12px;color:#94a3b8;">
            Turning reports into insights
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

page = st.sidebar.radio(
    "EXPLORE",
    [
        "🏠 Dashboard",
        "📊 Analysis",
        "📝 Report Problem",
        "💡 Insights"
    ]
)


# ---------------- FILTERS ----------------

filtered_df = df.copy()

if not df.empty:

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔎 DATA FILTERS")

    problems = sorted(
        df["Problem"].unique().tolist()
    )

    locations = sorted(
        df["Location"].unique().tolist()
    )

    selected_problems = st.sidebar.multiselect(
        "Problem",
        problems
    )

    selected_locations = st.sidebar.multiselect(
        "Location",
        locations
    )

    severity_range = st.sidebar.slider(
        "Severity",
        1,
        5,
        (1, 5)
    )

    if selected_problems:
        filtered_df = filtered_df[
            filtered_df["Problem"].isin(
                selected_problems
            )
        ]

    if selected_locations:
        filtered_df = filtered_df[
            filtered_df["Location"].isin(
                selected_locations
            )
        ]

    filtered_df = filtered_df[
        filtered_df["Severity"].between(
            severity_range[0],
            severity_range[1]
        )
    ]

st.sidebar.markdown("---")

st.sidebar.caption(
    "Anonymous student reporting • Data-driven analysis"
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "🏠 Dashboard":

    st.markdown(
        """
        <div class="hero">
            <div class="hero-small">CAMPUS INTELLIGENCE PLATFORM</div>
            <h1>Campus Problem Analysis</h1>
            <p>
                Turning everyday campus problems into actionable insights.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if df.empty:
        st.info(
            "No reports available yet. Submit the first campus report!"
        )
        st.stop()

    if filtered_df.empty:
        st.warning(
            "No reports match the selected filters."
        )
        st.stop()

    priority_data = calculate_priority(filtered_df)

    pulse, pulse_text = campus_pulse(priority_data)

    # Campus Pulse

    st.markdown(
        f"""
        <div class="pulse">
            <div class="pulse-title">CAMPUS PULSE</div>
            <div class="pulse-status">{pulse}</div>
            <div class="pulse-description">
                {pulse_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Metrics

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Total Reports</div>
                <div class="metric-value">{len(filtered_df)}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        avg = filtered_df["Severity"].mean()

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Average Severity</div>
                <div class="metric-value">{avg:.1f}<span style="font-size:15px;color:#64748b;"> / 5</span></div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:

        top_problem = (
            filtered_df["Problem"]
            .value_counts()
            .idxmax()
        )

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Top Issue</div>
                <div class="metric-value" style="font-size:22px;">
                    {top_problem}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:

        location_count = (
            filtered_df["Location"]
            .nunique()
        )

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Affected Areas</div>
                <div class="metric-value">{location_count}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Problem of week

    st.markdown(
        '<div class="section-title">🏆 Problem of the Week</div>',
        unsafe_allow_html=True
    )

    top = priority_data.iloc[0]

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-label">Highest Priority</div>
                <div class="insight-value">
                    {priority_data.index[0]}
                </div>
                <div class="insight-text">
                    {top["Priority"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-label">Priority Score</div>
                <div class="insight-value">
                    {top["Priority Score"]:.2f}
                </div>
                <div class="insight-text">
                    Based on frequency + severity
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-label">Reports</div>
                <div class="insight-value">
                    {int(top["Reports"])}
                </div>
                <div class="insight-text">
                    Student reports for this issue
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Priority Radar

    st.markdown(
        '<div class="section-title">🚨 Priority Radar</div>',
        unsafe_allow_html=True
    )

    display_priority = priority_data.copy()

    display_priority = display_priority[
        [
            "Reports",
            "Average_Severity",
            "Priority Score",
            "Priority"
        ]
    ]

    st.dataframe(
        display_priority.round(2),
        use_container_width=True
    )

    # Charts

    st.markdown(
        '<div class="section-title">📊 Campus Overview</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("#### 📌 Problem Frequency")

        counts = (
            filtered_df["Problem"]
            .value_counts()
            .sort_values()
        )

        st.bar_chart(counts)

    with col2:

        st.markdown("#### ⚠️ Severity Distribution")

        severity = (
            filtered_df["Severity"]
            .value_counts()
            .sort_index()
        )

        st.bar_chart(severity)

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("#### 📍 Campus Hotspots")

        location_counts = (
            filtered_df["Location"]
            .value_counts()
            .head(5)
        )

        for location, count in location_counts.items():

            avg_location = (
                filtered_df[
                    filtered_df["Location"] == location
                ]["Severity"]
                .mean()
            )

            st.markdown(
                f"""
                <div class="hotspot" style="margin-bottom:10px;">
                    <div class="hotspot-title">📍 {location}</div>
                    <div class="hotspot-number">{count}</div>
                    <div class="hotspot-small">
                        reports • Avg severity {avg_location:.1f}/5
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    with col2:

        st.markdown("#### 🕐 When Are Problems Reported?")

        time_counts = (
            filtered_df["Time"]
            .value_counts()
        )

        st.bar_chart(time_counts)

    # Trend

    st.markdown(
        '<div class="section-title">📈 Campus Trend</div>',
        unsafe_allow_html=True
    )

    trend_df = filtered_df.dropna(
        subset=["Date"]
    ).copy()

    if not trend_df.empty:

        trend_df["Date"] = pd.to_datetime(
            trend_df["Date"]
        )

        daily = (
            trend_df.groupby("Date")
            .size()
            .rename("Reports")
        )

        st.line_chart(daily)

        st.markdown(
            f"""
            <div class="tip-box">
                <b>Trend Insight</b><br>
                {trend_message(filtered_df)}
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.info(
            "Trend will appear when reports have valid dates."
        )


# ============================================================
# ANALYSIS
# ============================================================

elif page == "📊 Analysis":

    st.markdown(
        """
        <div class="hero">
            <div class="hero-small">DATA EXPLORATION</div>
            <h1>Detailed Analysis</h1>
            <p>
                Explore frequency, severity, location and time patterns.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if filtered_df.empty:
        st.warning("No data available.")
        st.stop()

    priority = calculate_priority(filtered_df)

    st.markdown(
        '<div class="section-title">🚨 Smart Priority Analysis</div>',
        unsafe_allow_html=True
    )

    st.dataframe(
        priority.round(2),
        use_container_width=True
    )

    highest = priority.iloc[0]

    st.success(
        f"Highest priority problem: "
        f"**{priority.index[0]}** — {highest['Priority']}"
    )

    # Problem Location

    st.markdown(
        '<div class="section-title">📍 Problem × Location</div>',
        unsafe_allow_html=True
    )

    problem_location = pd.crosstab(
        filtered_df["Problem"],
        filtered_df["Location"]
    )

    st.dataframe(
        problem_location,
        use_container_width=True
    )

    # Location analysis

    st.markdown(
        '<div class="section-title">📍 Location Analysis</div>',
        unsafe_allow_html=True
    )

    location_analysis = (
        filtered_df
        .groupby("Location")
        .agg(
            Reports=("Problem", "count"),
            Average_Severity=("Severity", "mean")
        )
        .sort_values(
            "Reports",
            ascending=False
        )
    )

    st.dataframe(
        location_analysis.round(2),
        use_container_width=True
    )

    # Time

    st.markdown(
        '<div class="section-title">🕐 Time Analysis</div>',
        unsafe_allow_html=True
    )

    time_analysis = (
        filtered_df["Time"]
        .value_counts()
    )

    st.bar_chart(time_analysis)

    # Trend

    st.markdown(
        '<div class="section-title">📈 Reports Over Time</div>',
        unsafe_allow_html=True
    )

    trend = filtered_df.dropna(
        subset=["Date"]
    ).copy()

    if not trend.empty:

        trend["Date"] = pd.to_datetime(
            trend["Date"]
        )

        daily = (
            trend.groupby("Date")
            .size()
            .rename("Reports")
        )

        st.line_chart(daily)

    else:

        st.info(
            "Add valid dates to reports to see trends."
        )

    # Download

    csv = filtered_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "⬇️ Download Filtered Data",
        csv,
        "campus_reports.csv",
        "text/csv"
    )


# ============================================================
# REPORT PROBLEM
# ============================================================

elif page == "📝 Report Problem":

    st.markdown(
        """
        <div class="hero">
            <div class="hero-small">STUDENT REPORTING</div>
            <h1>Something bothering you?</h1>
            <p>
                Report it. We'll turn campus reports into useful insights.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="tip-box">
            <b>🔒 Anonymous Reporting</b><br>
            No personal information is required. Describe the issue clearly
            so that it can be analyzed properly.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("")

    with st.form("report_form"):

        st.markdown(
            '<div class="section-title">Tell us about the problem</div>',
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)

        with col1:

            problem = st.selectbox(
                "What is the problem?",
                [
                    "Wi-Fi",
                    "Canteen",
                    "Lab PC",
                    "Library",
                    "Water",
                    "Electricity",
                    "Cleanliness",
                    "Other"
                ]
            )

        with col2:

            location = st.selectbox(
                "Where is it happening?",
                [
                    "Block A",
                    "Block B",
                    "Library",
                    "Canteen",
                    "Computer Lab",
                    "Hostel",
                    "Other"
                ]
            )

        time = st.selectbox(
            "When does it usually happen?",
            [
                "8 AM - 10 AM",
                "10 AM - 12 PM",
                "12 PM - 2 PM",
                "2 PM - 4 PM",
                "4 PM - 6 PM",
                "6 PM - 8 PM"
            ]
        )

        severity = st.slider(
            "How serious is the problem?",
            1,
            5,
            3
        )

        severity_text = {
            1: "Very Low",
            2: "Low",
            3: "Moderate",
            4: "High",
            5: "Very High"
        }

        st.caption(
            f"Selected severity: **{severity_text[severity]}**"
        )

        description = st.text_area(
            "Tell us more",
            placeholder=(
                "Example: Wi-Fi becomes very slow during afternoon "
                "classes in the computer lab."
            )
        )

        report_date = date.today().strftime(
            "%d-%m-%Y"
        )

        st.caption(
            f"📅 Report date: {report_date}"
        )

        submitted = st.form_submit_button(
            "Submit Report →",
            use_container_width=True
        )

        if submitted:

            if description.strip() == "":

                st.warning(
                    "Please describe the problem before submitting."
                )

            else:

                sheet.append_row(
                    [
                        problem,
                        location,
                        time,
                        severity,
                        description,
                        report_date
                    ]
                )

                st.success(
                    "✓ Report received! "
                    "Thanks for helping us understand campus problems better."
                )

                st.rerun()


# ============================================================
# INSIGHTS
# ============================================================

elif page == "💡 Insights":

    st.markdown(
        """
        <div class="hero">
            <div class="hero-small">DATA-DRIVEN INSIGHTS</div>
            <h1>What needs attention?</h1>
            <p>
                Important observations generated from the current reports.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if filtered_df.empty:
        st.warning("No data available.")
        st.stop()

    priority = calculate_priority(filtered_df)

    top_problem = priority.index[0]
    top_row = priority.iloc[0]

    top_location = (
        filtered_df["Location"]
        .value_counts()
        .idxmax()
    )

    peak_time = (
        filtered_df["Time"]
        .value_counts()
        .idxmax()
    )

    avg_severity = (
        filtered_df["Severity"]
        .mean()
    )

    # Main insight cards

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-label">Priority Issue</div>
                <div class="insight-value">{top_problem}</div>
                <div class="insight-text">
                    {top_row["Priority"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-label">Most Affected Area</div>
                <div class="insight-value">{top_location}</div>
                <div class="insight-text">
                    Highest number of reports
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:

        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-label">Peak Reporting Time</div>
                <div class="insight-value">{peak_time}</div>
                <div class="insight-text">
                    Most reports received
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:

        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-label">Average Severity</div>
                <div class="insight-value">{avg_severity:.1f}/5</div>
                <div class="insight-text">
                    Across current reports
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Main insight

    st.markdown(
        '<div class="section-title">🧠 Key Finding</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-label">CURRENT PRIORITY</div>
            <div class="insight-value">
                {top_problem}
            </div>
            <div class="insight-text" style="font-size:15px;">
                This issue currently has the highest analytical priority
                based on its reporting frequency and average severity.
                Its calculated priority score is
                <b>{top_row["Priority Score"]:.2f}</b>.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Recommendation

    st.markdown(
        '<div class="section-title">💡 Recommended Action</div>',
        unsafe_allow_html=True
    )

    recommendations = {

        "Wi-Fi":
            "IT team should check network connectivity, access points and bandwidth in the affected area.",

        "Canteen":
            "Queue management and service capacity should be reviewed during the busiest reporting period.",

        "Lab PC":
            "Technical team should inspect slow or faulty computers and check system performance.",

        "Library":
            "Seating availability and library resources should be reviewed during peak usage hours.",

        "Water":
            "Facilities team should inspect water supply points and identify recurring supply issues.",

        "Electricity":
            "Maintenance team should inspect electrical infrastructure in the affected location.",

        "Cleanliness":
            "Cleaning frequency and maintenance schedules should be reviewed."
    }

    recommendation = recommendations.get(
        top_problem,
        "Administration should review this issue and identify an appropriate solution."
    )

    st.markdown(
        f"""
        <div class="tip-box">
            <b>Suggested Action</b><br>
            {recommendation}
        </div>
        """,
        unsafe_allow_html=True
    )

    # Trend insight

    st.markdown(
        '<div class="section-title">📈 Trend Insight</div>',
        unsafe_allow_html=True
    )

    st.info(
        trend_message(filtered_df)
    )

    # Method note

    st.markdown(
        '<div class="section-title">ℹ️ About this analysis</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="insight-card">
            Priority is calculated using two factors:
            <br><br>
            <b>Frequency</b> — how often the problem is reported.
            <br>
            <b>Severity</b> — how serious the reported problem is.
            <br><br>
            These factors are combined into an analytical priority score.
            This system is <b>not an ML prediction model</b>.
        </div>
        """,
        unsafe_allow_html=True
    )


# ---------------- FOOTER ----------------

st.markdown(
    """
    <div class="footer">
        Campus Intelligence • Campus Problem Analysis<br>
        Student Project • Data-driven campus improvement
    </div>
    """,
    unsafe_allow_html=True
)