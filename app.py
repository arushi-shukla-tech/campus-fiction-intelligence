import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(
    page_title="Campus Problem Analysis",
    page_icon="📊",
    layout="wide"
)

# ---------- STYLE ----------

st.markdown("""
<style>

.main-title {
    font-size: 42px;
    font-weight: 700;
    margin-bottom: 4px;
}

.subtitle {
    font-size: 17px;
    color: #666;
    margin-bottom: 20px;
}

.dashboard-card {
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #e5e5e5;
    background-color: #ffffff;
}

.card-title {
    font-size: 14px;
    color: #666;
}

.card-value {
    font-size: 27px;
    font-weight: 700;
    margin-top: 5px;
}

.section-title {
    font-size: 25px;
    font-weight: 650;
    margin-top: 32px;
    margin-bottom: 15px;
}

.insight-box {
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #ddd;
    margin-top: 10px;
}

</style>
""", unsafe_allow_html=True)


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


# ---------- HEADER ----------

st.markdown(
    '<div class="main-title">Campus Problem Analysis</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Analysis of common college problems using student reports'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# ---------- DASHBOARD ----------

st.markdown(
    '<div class="section-title">📊 Dashboard Overview</div>',
    unsafe_allow_html=True
)

if not df.empty:

    total_reports = len(df)

    high_severity = len(
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

    total_reports = 0
    high_severity = 0
    top_problem = "-"
    top_location = "-"


c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        f"""
        <div class="dashboard-card">
        <div class="card-title">TOTAL REPORTS</div>
        <div class="card-value">{total_reports}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        f"""
        <div class="dashboard-card">
        <div class="card-title">HIGH SEVERITY</div>
        <div class="card-value">{high_severity}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c3:
    st.markdown(
        f"""
        <div class="dashboard-card">
        <div class="card-title">TOP PROBLEM</div>
        <div class="card-value">{top_problem}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c4:
    st.markdown(
        f"""
        <div class="dashboard-card">
        <div class="card-title">TOP LOCATION</div>
        <div class="card-value">{top_location}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ---------- FILTERS ----------

if not df.empty:

    st.markdown(
        '<div class="section-title">🔎 Explore Reports</div>',
        unsafe_allow_html=True
    )

    f1, f2, f3 = st.columns(3)

    with f1:

        selected_problem = st.selectbox(
            "Problem",
            ["All"] + sorted(
                df["Problem"].unique().tolist()
            )
        )

    with f2:

        selected_location = st.selectbox(
            "Location",
            ["All"] + sorted(
                df["Location"].unique().tolist()
            )
        )

    with f3:

        selected_severity = st.selectbox(
            "Severity",
            ["All", 1, 2, 3, 4, 5]
        )

    filtered_df = df.copy()

    if selected_problem != "All":

        filtered_df = filtered_df[
            filtered_df["Problem"] == selected_problem
        ]

    if selected_location != "All":

        filtered_df = filtered_df[
            filtered_df["Location"] == selected_location
        ]

    if selected_severity != "All":

        filtered_df = filtered_df[
            filtered_df["Severity"] == selected_severity
        ]

    st.write(
        f"Showing **{len(filtered_df)}** report(s)"
    )

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )


# ---------- ANALYSIS ----------

if not df.empty:

    # Priority calculation

    result = []

    for problem in df["Problem"].unique():

        values = df[
            df["Problem"] == problem
        ]["Severity"]

        reports = len(values)

        average_severity = values.mean()

        priority_score = (
            reports * average_severity
        )

        if priority_score >= 12:
            level = "Critical"

        elif priority_score >= 8:
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
            "Level"
        ]
    )

    analysis = analysis.sort_values(
        "Priority Score",
        ascending=False
    )


    # ---------- PRIORITY ----------

    st.markdown(
        '<div class="section-title">🚨 Priority Analysis</div>',
        unsafe_allow_html=True
    )

    st.dataframe(
        analysis,
        use_container_width=True,
        hide_index=True
    )


    # ---------- TOP PRIORITY ----------

    highest = analysis.iloc[0]

    highest_problem = highest["Problem"]

    highest_location = (
        df[df["Problem"] == highest_problem]
        ["Location"]
        .value_counts()
        .idxmax()
    )

    st.markdown(
        '<div class="section-title">🎯 Current Priority</div>',
        unsafe_allow_html=True
    )

    st.success(
        f"{highest_problem} currently has the highest "
        f"priority score of {highest['Priority Score']}. "
        f"Most reports for this problem come from "
        f"{highest_location}."
    )


    # ---------- CHARTS ----------

    st.markdown(
        '<div class="section-title">📈 Problem Trends</div>',
        unsafe_allow_html=True
    )

    chart1, chart2 = st.columns(2)

    with chart1:

        st.write("Reports by Problem")

        problem_count = (
            df["Problem"]
            .value_counts()
        )

        st.bar_chart(
            problem_count
        )

    with chart2:

        st.write("Reports by Location")

        location_count = (
            df["Location"]
            .value_counts()
        )

        st.bar_chart(
            location_count
        )


    # ---------- SEVERITY ----------

    st.markdown(
        '<div class="section-title">⚠️ Severity Distribution</div>',
        unsafe_allow_html=True
    )

    severity_count = (
        df["Severity"]
        .value_counts()
        .sort_index()
    )

    st.bar_chart(
        severity_count
    )


    # ---------- TIME ----------

    st.markdown(
        '<div class="section-title">⏰ Peak Reporting Time</div>',
        unsafe_allow_html=True
    )

    time_count = (
        df["Time"]
        .value_counts()
    )

    st.bar_chart(
        time_count
    )

    peak_time = time_count.idxmax()

    st.info(
        f"Most reports are received around **{peak_time}**."
    )


    # ---------- PATTERNS ----------

    st.markdown(
        '<div class="section-title">🔍 Problem Patterns</div>',
        unsafe_allow_html=True
    )

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


    # ---------- RECOMMENDATION ----------

    recommendations = {

        "Wi-Fi":
        "Wi-Fi should be checked in areas where reports are frequent.",

        "Canteen Queue":
        "Queue management should be improved during busy hours.",

        "Slow Computer":
        "Lab computers should be checked and maintained regularly.",

        "No Seats":
        "Library seating should be increased during peak hours.",

        "Water Problem":
        "Drinking water facilities should be checked regularly.",

        "Electricity":
        "Electrical equipment and power usage should be checked.",

        "Noise":
        "The source of noise should be identified and managed."
    }

    st.markdown(
        '<div class="section-title">💡 Recommendation</div>',
        unsafe_allow_html=True
    )

    st.info(
        recommendations.get(
            highest_problem,
            "The highest priority problem needs attention."
        )
    )


    # ---------- PREDICTION ----------

    st.markdown(
        '<div class="section-title">🔮 Problem Prediction</div>',
        unsafe_allow_html=True
    )

    st.write(
        f"Based on the current reports, "
        f"**{highest_problem}** is most likely to "
        f"need attention next."
    )

    st.caption(
        "This is a priority-based prediction using "
        "the current student reports. More real college "
        "data can improve future predictions."
    )


    # ---------- DOWNLOAD ----------

    st.markdown(
        '<div class="section-title">📥 Download Data</div>',
        unsafe_allow_html=True
    )

    csv_data = df.to_csv(
        index=False
    )

    st.download_button(
        "Download Reports CSV",
        csv_data,
        "campus_reports.csv",
        "text/csv"
    )


# ---------- REPORT FORM ----------

st.markdown(
    '<div class="section-title">📝 Report a Problem</div>',
    unsafe_allow_html=True
)

p1, p2 = st.columns(2)

with p1:

    problem = st.selectbox(
        "Select Problem",
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
        "Select Location",
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
    "Describe the problem"
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
            "Report submitted successfully."
        )

        st.rerun()

    else:

        st.warning(
            "Please describe the problem."
        )