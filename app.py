import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(
    page_title="Campus Problem Analysis",
    page_icon="📊",
    layout="wide"
)

# ---------- GOOGLE SHEETS ----------

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scopes
)

client = gspread.authorize(credentials)
sheet = client.open("Campus Reports").sheet1


# ---------- LOAD DATA ----------

records = sheet.get_all_records()

df = pd.DataFrame(
    records,
    columns=[
        "Problem",
        "Location",
        "Time",
        "Severity",
        "Description"
    ]
)

if not df.empty:

    df["Severity"] = pd.to_numeric(
        df["Severity"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["Problem", "Location", "Severity"]
    )

    df["Severity"] = df["Severity"].astype(int)


# ---------- STYLE ----------

st.markdown("""
<style>

.block-container {
    padding-top: 2rem;
    max-width: 1200px;
}

.hero {
    padding: 30px;
    border-radius: 18px;
    background: linear-gradient(
        135deg,
        #eef2ff,
        #f8fafc
    );
    border: 1px solid #e5e7eb;
    margin-bottom: 25px;
}

.hero-title {
    font-size: 42px;
    font-weight: 750;
    margin-bottom: 8px;
}

.hero-text {
    font-size: 17px;
    color: #64748b;
}

.stat-card {
    padding: 22px;
    border-radius: 15px;
    border: 1px solid #e5e7eb;
    background: white;
    min-height: 115px;
}

.stat-label {
    font-size: 13px;
    color: #64748b;
    font-weight: 600;
    text-transform: uppercase;
}

.stat-number {
    font-size: 29px;
    font-weight: 750;
    margin-top: 8px;
}

.section-title {
    font-size: 25px;
    font-weight: 700;
    margin-top: 30px;
    margin-bottom: 15px;
}

.info-card {
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #e5e7eb;
    background: #f8fafc;
}

.footer {
    text-align: center;
    color: #64748b;
    padding: 30px 0 10px;
}

</style>
""", unsafe_allow_html=True)


# ---------- SIDEBAR ----------

st.sidebar.title("📊 Campus Analysis")

st.sidebar.caption(
    "Student Problem Monitoring System"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "📊 Analysis",
        "📝 Report Problem",
        "💡 Insights"
    ]
)

st.sidebar.divider()

st.sidebar.caption(
    "Data source: Campus Reports"
)


# ---------- DASHBOARD ----------

if page == "🏠 Dashboard":

    st.markdown("""
    <div class="hero">
        <div class="hero-title">
            Campus Problem Analysis
        </div>
        <div class="hero-text">
            A data-driven dashboard for understanding
            common problems reported by students.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not df.empty:

        total = len(df)

        high = len(
            df[df["Severity"] >= 4]
        )

        top_problem = (
            df["Problem"]
            .value_counts()
            .idxmax()
        )

        top_location = (
            df["Location"]
            .value_counts()
            .idxmax()
        )

    else:

        total = 0
        high = 0
        top_problem = "-"
        top_location = "-"


    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">
                    Total Reports
                </div>
                <div class="stat-number">
                    {total}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">
                    High Severity
                </div>
                <div class="stat-number">
                    {high}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">
                    Top Problem
                </div>
                <div class="stat-number">
                    {top_problem}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c4:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">
                    Top Location
                </div>
                <div class="stat-number">
                    {top_location}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


    if not df.empty:

        st.markdown(
            '<div class="section-title">'
            '📈 Problem Overview'
            '</div>',
            unsafe_allow_html=True
        )

        a, b = st.columns(2)

        with a:

            st.write("Problems reported")

            st.bar_chart(
                df["Problem"].value_counts()
            )

        with b:

            st.write("Affected locations")

            st.bar_chart(
                df["Location"].value_counts()
            )


        st.markdown(
            '<div class="section-title">'
            '⚠️ Severity Overview'
            '</div>',
            unsafe_allow_html=True
        )

        st.bar_chart(
            df["Severity"]
            .value_counts()
            .sort_index()
        )


    else:

        st.info(
            "No reports available yet. "
            "Use 'Report Problem' to add one."
        )


# ---------- ANALYSIS ----------

elif page == "📊 Analysis":

    st.title("📊 Detailed Analysis")

    if df.empty:

        st.info("No data available for analysis.")

    else:

        result = []

        for problem in df["Problem"].unique():

            values = df[
                df["Problem"] == problem
            ]["Severity"]

            reports = len(values)

            average = values.mean()

            priority = reports * average

            if priority >= 12:
                level = "Critical"

            elif priority >= 8:
                level = "High"

            elif priority >= 5:
                level = "Medium"

            else:
                level = "Low"

            result.append([
                problem,
                reports,
                round(average, 2),
                round(priority, 2),
                level
            ])

        analysis = pd.DataFrame(
            result,
            columns=[
                "Problem",
                "Reports",
                "Average Severity",
                "Priority Score",
                "Level"
            ]
        )

        analysis = analysis.sort_values(
            "Priority Score",
            ascending=False
        )

        st.subheader("🚨 Priority Ranking")

        st.dataframe(
            analysis,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("🔍 Problem Patterns")

        patterns = (
            df.groupby(
                ["Problem", "Location"]
            )
            .size()
            .reset_index(
                name="Reports"
            )
            .sort_values(
                "Reports",
                ascending=False
            )
        )

        st.dataframe(
            patterns,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("⏰ Reporting Time")

        time_count = df["Time"].value_counts()

        st.bar_chart(time_count)

        st.info(
            f"Peak reporting time: "
            f"{time_count.idxmax()}"
        )

        st.download_button(
            "📥 Download Reports CSV",
            df.to_csv(index=False),
            "campus_reports.csv",
            "text/csv"
        )


# ---------- REPORT PROBLEM ----------

elif page == "📝 Report Problem":

    st.title("📝 Report a Campus Problem")

    st.write(
        "Submit a problem anonymously. "
        "Your report will be added to the analysis."
    )

    st.divider()

    p1, p2 = st.columns(2)

    with p1:

        problem = st.selectbox(
            "Problem",
            [
                "Wi-Fi",
                "Canteen Queue",
                "Slow Computer",
                "No Seats",
                "Water Problem",
                "Electricity",
                "Noise",
                "Other"
            ]
        )

    with p2:

        location = st.selectbox(
            "Location",
            [
                "Block A",
                "Block B",
                "Canteen",
                "Library",
                "Lab 1",
                "Lab 2",
                "Other"
            ]
        )

    time = st.selectbox(
        "Time",
        [
            "8:00 AM",
            "9:00 AM",
            "10:00 AM",
            "11:00 AM",
            "12:00 PM",
            "1:00 PM",
            "2:00 PM",
            "3:00 PM",
            "4:00 PM",
            "5:00 PM"
        ]
    )

    severity = st.slider(
        "Severity",
        1,
        5,
        3
    )

    description = st.text_area(
        "Describe the problem",
        placeholder=(
            "Example: Wi-Fi becomes very slow "
            "during lunch time."
        )
    )

    if st.button(
        "Submit Report",
        type="primary"
    ):

        if description.strip():

            sheet.append_row([
                problem,
                location,
                time,
                severity,
                description
            ])

            st.success(
                "Report submitted successfully!"
            )

            st.rerun()

        else:

            st.warning(
                "Please describe the problem."
            )


# ---------- INSIGHTS ----------

elif page == "💡 Insights":

    st.title("💡 Smart Insights")

    if df.empty:

        st.info(
            "Add some reports to generate insights."
        )

    else:

        problem_count = (
            df["Problem"]
            .value_counts()
        )

        location_count = (
            df["Location"]
            .value_counts()
        )

        severity_count = (
            df["Severity"]
            .value_counts()
        )

        time_count = (
            df["Time"]
            .value_counts()
        )

        top_problem = problem_count.idxmax()
        top_location = location_count.idxmax()
        peak_time = time_count.idxmax()

        high_count = len(
            df[df["Severity"] >= 4]
        )

        st.markdown(
            '<div class="info-card">',
            unsafe_allow_html=True
        )

        st.subheader("Most Reported Problem")

        st.write(
            f"**{top_problem}** has the highest "
            f"number of student reports."
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


        st.markdown(
            '<div class="info-card">',
            unsafe_allow_html=True
        )

        st.subheader("Most Affected Location")

        st.write(
            f"**{top_location}** has received "
            f"the highest number of reports."
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


        st.markdown(
            '<div class="info-card">',
            unsafe_allow_html=True
        )

        st.subheader("Peak Reporting Time")

        st.write(
            f"Most reports are received around "
            f"**{peak_time}**."
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


        st.markdown(
            '<div class="info-card">',
            unsafe_allow_html=True
        )

        st.subheader("Severity Alert")

        st.write(
            f"There are **{high_count}** reports "
            f"with severity level 4 or 5."
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


        recommendations = {

            "Wi-Fi":
            "Check network performance in frequently affected areas.",

            "Canteen Queue":
            "Improve queue management during busy hours.",

            "Slow Computer":
            "Check and maintain computers in frequently affected labs.",

            "No Seats":
            "Consider increasing seating during peak hours.",

            "Water Problem":
            "Regularly inspect drinking water facilities.",

            "Electricity":
            "Inspect electrical equipment and power supply.",

            "Noise":
            "Identify and manage the main source of noise."
        }

        st.markdown(
            '<div class="section-title">'
            '💡 Recommended Action'
            '</div>',
            unsafe_allow_html=True
        )

        st.info(
            recommendations.get(
                top_problem,
                "The most reported problem should be investigated."
            )
        )

        st.caption(
            "Insights are generated from the reports currently "
            "available in the Campus Reports Google Sheet."
        )


# ---------- FOOTER ----------

st.markdown(
    '<div class="footer">'
    'Campus Problem Analysis • Student Data Dashboard'
    '</div>',
    unsafe_allow_html=True
)