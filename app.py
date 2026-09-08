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
    margin-bottom: 5px;
}

.subtitle {
    font-size: 18px;
    color: #666;
    margin-bottom: 25px;
}

.section-title {
    font-size: 25px;
    font-weight: 600;
    margin-top: 30px;
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


# Load reports from Google Sheet

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

    df = df.dropna(subset=["Problem", "Location", "Severity"])

    df["Severity"] = df["Severity"].astype(int)


# Page heading

st.markdown(
    '<div class="main-title">Campus Problem Analysis</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Analysis of common college problems using student reports</div>',
    unsafe_allow_html=True
)

st.divider()


# Dashboard

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Reports", len(df))

if not df.empty:

    c2.metric(
        "High Severity",
        len(df[df["Severity"] >= 4])
    )

    c3.metric(
        "Top Problem",
        df["Problem"].value_counts().idxmax()
    )

    c4.metric(
        "Top Location",
        df["Location"].value_counts().idxmax()
    )

else:

    c2.metric("High Severity", 0)
    c3.metric("Top Problem", "-")
    c4.metric("Top Location", "-")


# Explore reports

st.markdown(
    '<div class="section-title">Explore Reports</div>',
    unsafe_allow_html=True
)

if not df.empty:

    f1, f2 = st.columns(2)

    with f1:
        selected_problem = st.selectbox(
            "Filter by Problem",
            ["All"] + sorted(
                df["Problem"].unique().tolist()
            )
        )

    with f2:
        selected_location = st.selectbox(
            "Filter by Location",
            ["All"] + sorted(
                df["Location"].unique().tolist()
            )
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

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info("No reports available yet.")


# Problem Analysis

st.markdown(
    '<div class="section-title">Problem Analysis</div>',
    unsafe_allow_html=True
)

if not df.empty:

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

else:

    st.info("Analysis will appear after reports are submitted.")


# Problem-wise reports

if not df.empty:

    st.markdown(
        '<div class="section-title">Problem-wise Reports</div>',
        unsafe_allow_html=True
    )

    st.bar_chart(
        df["Problem"].value_counts()
    )


# Severity analysis

if not df.empty:

    st.markdown(
        '<div class="section-title">Severity Analysis</div>',
        unsafe_allow_html=True
    )

    st.bar_chart(
        df["Severity"].value_counts().sort_index()
    )


# Location analysis

if not df.empty:

    st.markdown(
        '<div class="section-title">Location-wise Reports</div>',
        unsafe_allow_html=True
    )

    st.bar_chart(
        df["Location"].value_counts()
    )


# Problem patterns

if not df.empty:

    st.markdown(
        '<div class="section-title">Problem Patterns</div>',
        unsafe_allow_html=True
    )

    patterns = (
        df.groupby(["Problem", "Location"])
        .size()
        .reset_index(name="Reports")
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


# Time analysis

if not df.empty:

    st.markdown(
        '<div class="section-title">Time Analysis</div>',
        unsafe_allow_html=True
    )

    time_count = df["Time"].value_counts()

    st.bar_chart(time_count)

    peak_time = time_count.idxmax()

    st.info(
        f"Most reports are being received around {peak_time}."
    )


# Smart insight

if not df.empty:

    top_problem = analysis.iloc[0]["Problem"]

    top_location = df[
        df["Problem"] == top_problem
    ]["Location"].value_counts().idxmax()

    st.markdown(
        '<div class="section-title">Smart Insight</div>',
        unsafe_allow_html=True
    )

    st.success(
        f"{top_problem} is the highest-priority problem, "
        f"with the most reports coming from {top_location}."
    )


# Recommendation

recommendations = {
    "Wi-Fi": "Wi-Fi should be checked in the areas where reports are frequent.",
    "Canteen Queue": "Queue management should be improved during busy hours.",
    "Slow Computer": "Lab computers should be checked and maintained regularly.",
    "No Seats": "Library seating should be increased during peak hours.",
    "Water Problem": "Drinking water facilities should be checked regularly.",
    "Electricity": "Electrical equipment and power usage should be checked.",
    "Noise": "The source of noise should be identified and managed."
}

if not df.empty:

    st.markdown(
        '<div class="section-title">Recommendation</div>',
        unsafe_allow_html=True
    )

    st.info(
        recommendations.get(
            top_problem,
            "The highest priority problem needs attention."
        )
    )


# Problem prediction

if not df.empty:

    st.markdown(
        '<div class="section-title">Problem Prediction</div>',
        unsafe_allow_html=True
    )

    prediction = analysis.iloc[0]

    st.write(
        f"Based on the current reports, "
        f"{prediction['Problem']} is most likely to need attention next."
    )

    st.write(
        f"Current priority score: "
        f"{prediction['Priority Score']}"
    )

    st.caption(
        "This is a priority-based prediction using the current "
        "student reports. More real college data can improve "
        "future predictions."
    )


# Download reports

if not df.empty:

    st.markdown(
        '<div class="section-title">Download Analysis</div>',
        unsafe_allow_html=True
    )

    csv_data = df.to_csv(index=False)

    st.download_button(
        "Download Reports",
        csv_data,
        "campus_reports.csv",
        "text/csv"
    )


# Report a problem

st.markdown(
    '<div class="section-title">Report a Problem</div>',
    unsafe_allow_html=True
)

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