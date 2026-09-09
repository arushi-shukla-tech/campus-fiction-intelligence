import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(
    page_title="Campus Problem Analysis",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
.main-title {
    font-size: 42px;
    font-weight: 700;
}

.subtitle {
    font-size: 18px;
    color: #666;
    margin-bottom: 20px;
}

.section-title {
    font-size: 25px;
    font-weight: 600;
    margin-top: 30px;
    margin-bottom: 15px;
}

div[data-testid="stMetric"] {
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #ddd;
}
</style>
""", unsafe_allow_html=True)


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


# Title

st.markdown(
    '<div class="main-title">Campus Problem Analysis</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Analysis of common college problems using student reports</div>',
    unsafe_allow_html=True
)

st.divider()


# Dashboard summary

st.markdown(
    '<div class="section-title">Dashboard Overview</div>',
    unsafe_allow_html=True
)

c1, c2, c3, c4 = st.columns(4)

if not df.empty:

    total_reports = len(df)

    high_severity = len(
        df[df["Severity"] >= 4]
    )

    top_problem = df[
        "Problem"
    ].value_counts().idxmax()

    top_location = df[
        "Location"
    ].value_counts().idxmax()

else:

    total_reports = 0
    high_severity = 0
    top_problem = "-"
    top_location = "-"

c1.metric(
    "Total Reports",
    total_reports
)

c2.metric(
    "High Severity",
    high_severity
)

c3.metric(
    "Top Problem",
    top_problem
)

c4.metric(
    "Top Location",
    top_location
)


# Filters

if not df.empty:

    st.markdown(
        '<div class="section-title">Explore Reports</div>',
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

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )


# Charts

if not df.empty:

    st.markdown(
        '<div class="section-title">Problem Overview</div>',
        unsafe_allow_html=True
    )

    chart1, chart2 = st.columns(2)

    with chart1:

        st.write("Reports by Problem")

        problem_count = (
            df["Problem"]
            .value_counts()
        )

        st.bar_chart(problem_count)

    with chart2:

        st.write("Reports by Location")

        location_count = (
            df["Location"]
            .value_counts()
        )

        st.bar_chart(location_count)


    # Severity

    st.markdown(
        '<div class="section-title">Severity Analysis</div>',
        unsafe_allow_html=True
    )

    severity_count = (
        df["Severity"]
        .value_counts()
        .sort_index()
    )

    st.bar_chart(severity_count)


    # Priority analysis

    st.markdown(
        '<div class="section-title">Priority Analysis</div>',
        unsafe_allow_html=True
    )

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

    st.dataframe(
        analysis,
        use_container_width=True,
        hide_index=True
    )


    # Time analysis

    st.markdown(
        '<div class="section-title">Time Analysis</div>',
        unsafe_allow_html=True
    )

    time_count = (
        df["Time"]
        .value_counts()
    )

    st.bar_chart(time_count)

    peak_time = time_count.idxmax()

    st.info(
        f"Peak reporting time: {peak_time}"
    )


    # Smart insight

    st.markdown(
        '<div class="section-title">Smart Insight</div>',
        unsafe_allow_html=True
    )

    highest = analysis.iloc[0]

    highest_problem = highest["Problem"]

    highest_location = df[
        df["Problem"] == highest_problem
    ]["Location"].value_counts().idxmax()

    st.success(
        f"{highest_problem} currently has the highest "
        f"priority score. Most reports for this problem "
        f"come from {highest_location}."
    )


    # Recommendation

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
        '<div class="section-title">Recommendation</div>',
        unsafe_allow_html=True
    )

    st.info(
        recommendations.get(
            highest_problem,
            "The highest priority problem needs attention."
        )
    )


    # Prediction

    st.markdown(
        '<div class="section-title">Problem Prediction</div>',
        unsafe_allow_html=True
    )

    st.write(
        f"Based on the current reports, "
        f"{highest_problem} is most likely to need "
        f"attention next."
    )

    st.write(
        f"Current priority score: "
        f"{highest['Priority Score']}"
    )

    st.caption(
        "This is a priority-based prediction using "
        "the current student reports. More real college "
        "data can improve future predictions."
    )


    # Download

    st.markdown(
        '<div class="section-title">Download Reports</div>',
        unsafe_allow_html=True
    )

    csv_data = df.to_csv(index=False)

    st.download_button(
        "Download CSV",
        csv_data,
        "campus_reports.csv",
        "text/csv"
    )


# Report form

st.markdown(
    '<div class="section-title">Report a Problem</div>',
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


# Submit report

if st.button("Submit Report"):

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