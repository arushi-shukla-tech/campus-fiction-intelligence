import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(
    page_title="Campus Problem Analysis",
    page_icon="📊",
    layout="wide"
)

# Google Sheets connection

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


# Load data

records = sheet.get_all_records()

columns = [
    "Problem",
    "Location",
    "Time",
    "Severity",
    "Description"
]

df = pd.DataFrame(records, columns=columns)

if not df.empty:

    df["Severity"] = pd.to_numeric(
        df["Severity"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["Problem", "Location", "Severity"]
    )

    df["Severity"] = df["Severity"].astype(int)


# Styling

st.markdown("""
<style>

.block-container {
    padding-top: 2rem;
    max-width: 1200px;
}

.title {
    font-size: 42px;
    font-weight: 750;
    margin-bottom: 5px;
}

.subtitle {
    color: #64748b;
    font-size: 17px;
    margin-bottom: 30px;
}

.card {
    padding: 20px;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
    background: white;
    min-height: 115px;
}

.label {
    font-size: 13px;
    color: #64748b;
    font-weight: 600;
}

.value {
    font-size: 29px;
    font-weight: 750;
    margin-top: 8px;
}

.section {
    font-size: 25px;
    font-weight: 700;
    margin-top: 35px;
    margin-bottom: 15px;
}

.insight {
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #e5e7eb;
    background: #f8fafc;
    margin-bottom: 12px;
}

</style>
""", unsafe_allow_html=True)


# Sidebar

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


# ==================================================
# DASHBOARD
# ==================================================

if page == "🏠 Dashboard":

    st.markdown(
        '<div class="title">Campus Problem Analysis</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Understanding common campus problems through student reports.'
        '</div>',
        unsafe_allow_html=True
    )

    if df.empty:

        st.info(
            "No reports available. Add reports from Report Problem."
        )

    else:

        total = len(df)

        high = len(
            df[df["Severity"] >= 4]
        )

        average = round(
            df["Severity"].mean(),
            2
        )

        top_problem = (
            df["Problem"]
            .value_counts()
            .idxmax()
        )

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.markdown(
                f"""
                <div class="card">
                    <div class="label">TOTAL REPORTS</div>
                    <div class="value">{total}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c2:
            st.markdown(
                f"""
                <div class="card">
                    <div class="label">HIGH SEVERITY</div>
                    <div class="value">{high}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c3:
            st.markdown(
                f"""
                <div class="card">
                    <div class="label">AVERAGE SEVERITY</div>
                    <div class="value">{average}/5</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c4:
            st.markdown(
                f"""
                <div class="card">
                    <div class="label">TOP PROBLEM</div>
                    <div class="value">{top_problem}</div>
                </div>
                """,
                unsafe_allow_html=True
            )


        st.markdown(
            '<div class="section">📌 Problem Frequency</div>',
            unsafe_allow_html=True
        )

        problem_count = (
            df["Problem"]
            .value_counts()
        )

        st.bar_chart(problem_count)


        st.markdown(
            '<div class="section">⚠️ Severity Distribution</div>',
            unsafe_allow_html=True
        )

        severity_count = (
            df["Severity"]
            .value_counts()
            .sort_index()
        )

        st.bar_chart(severity_count)


        st.markdown(
            '<div class="section">📍 Location Overview</div>',
            unsafe_allow_html=True
        )

        location_count = (
            df["Location"]
            .value_counts()
        )

        st.bar_chart(location_count)


# ==================================================
# ANALYSIS
# ==================================================

elif page == "📊 Analysis":

    st.title("📊 Detailed Analysis")

    if df.empty:

        st.info(
            "No data available. Add some reports first."
        )

    else:

        # Priority analysis

        result = []

        for problem in df["Problem"].unique():

            problem_data = df[
                df["Problem"] == problem
            ]

            reports = len(problem_data)

            average_severity = (
                problem_data["Severity"].mean()
            )

            priority_score = (
                reports * average_severity
            )

            if priority_score >= 15:
                level = "Critical"

            elif priority_score >= 10:
                level = "High"

            elif priority_score >= 5:
                level = "Medium"

            else:
                level = "Low"

            result.append([
                problem,
                reports,
                round(average_severity, 2),
                round(priority_score, 2),
                level
            ])


        analysis = pd.DataFrame(
            result,
            columns=[
                "Problem",
                "Reports",
                "Average Severity",
                "Priority Score",
                "Priority Level"
            ]
        )

        analysis = analysis.sort_values(
            "Priority Score",
            ascending=False
        )


        st.subheader("🎯 Priority Ranking")

        st.dataframe(
            analysis,
            use_container_width=True,
            hide_index=True
        )


        # Problem and location

        st.subheader("📍 Problem × Location")

        problem_location = pd.crosstab(
            df["Problem"],
            df["Location"]
        )

        st.dataframe(
            problem_location,
            use_container_width=True
        )


        # Time analysis

        st.subheader("⏰ Reporting Time Pattern")

        time_count = (
            df["Time"]
            .value_counts()
        )

        st.bar_chart(time_count)


        peak_time = time_count.idxmax()

        st.info(
            f"⏰ Peak reporting time: **{peak_time}**"
        )


        # Location analysis

        st.subheader("📌 Location Analysis")

        location_analysis = (
            df.groupby("Location")
            .agg(
                Reports=("Problem", "count"),
                Average_Severity=("Severity", "mean")
            )
            .reset_index()
        )

        location_analysis[
            "Average_Severity"
        ] = location_analysis[
            "Average_Severity"
        ].round(2)

        location_analysis = location_analysis.sort_values(
            "Reports",
            ascending=False
        )

        st.dataframe(
            location_analysis,
            use_container_width=True,
            hide_index=True
        )


        # Download

        st.download_button(
            "📥 Download Analysis CSV",
            analysis.to_csv(index=False),
            "campus_analysis.csv",
            "text/csv"
        )


# ==================================================
# REPORT PROBLEM
# ==================================================

elif page == "📝 Report Problem":

    st.title("📝 Report a Campus Problem")

    st.write(
        "Submit a problem anonymously."
    )

    st.divider()


    col1, col2 = st.columns(2)

    with col1:

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


    with col2:

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
        placeholder="Example: Wi-Fi becomes slow during lunch time."
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


# ==================================================
# INSIGHTS
# ==================================================

elif page == "💡 Insights":

    st.title("💡 Smart Insights")

    if df.empty:

        st.info(
            "Add reports to generate insights."
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
            f"""
            <div class="insight">
                <b>🚨 Most Reported Problem</b><br><br>
                {top_problem} is the most frequently reported problem.
            </div>
            """,
            unsafe_allow_html=True
        )


        st.markdown(
            f"""
            <div class="insight">
                <b>📍 Problem Hotspot</b><br><br>
                {top_location} has the highest number of reports.
            </div>
            """,
            unsafe_allow_html=True
        )


        st.markdown(
            f"""
            <div class="insight">
                <b>⏰ Peak Reporting Time</b><br><br>
                Most reports are associated with {peak_time}.
            </div>
            """,
            unsafe_allow_html=True
        )


        st.markdown(
            f"""
            <div class="insight">
                <b>⚠️ Severity Alert</b><br><br>
                {high_count} reports have severity level 4 or 5.
            </div>
            """,
            unsafe_allow_html=True
        )


        recommendations = {

            "Wi-Fi":
                "Check network performance in frequently affected areas.",

            "Canteen Queue":
                "Improve queue management during busy hours.",

            "Slow Computer":
                "Inspect frequently affected computers in the labs.",

            "No Seats":
                "Analyze peak library usage and consider additional seating.",

            "Water Problem":
                "Regularly inspect drinking-water facilities.",

            "Electricity":
                "Inspect electrical equipment and power supply.",

            "Noise":
                "Identify and manage the main source of noise.",

            "Other":
                "Investigate the most frequently reported problem."
        }


        st.subheader("💡 Recommended Action")

        st.info(
            recommendations.get(
                top_problem,
                "Investigate the most frequently reported problem."
            )
        )


        st.caption(
            "Insights are generated from the reports currently "
            "available in the Campus Reports Google Sheet."
        )


# Footer

st.divider()

st.caption(
    "Campus Problem Analysis • Student Data Science Project"
)