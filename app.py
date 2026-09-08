import streamlit as st
import pandas as pd

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

data = {
    "Problem": [
        "Wi-Fi", "Canteen Queue", "Slow Computer",
        "No Seats", "Wi-Fi", "Water Problem",
        "Canteen Queue", "Slow Computer",
        "Wi-Fi", "No Seats"
    ],
    "Location": [
        "Block A", "Canteen", "Lab 2", "Library",
        "Block A", "Block B", "Canteen", "Lab 2",
        "Block B", "Library"
    ],
    "Time": [
        "10:30 AM", "1:00 PM", "11:00 AM", "4:00 PM",
        "1:15 PM", "12:30 PM", "1:10 PM", "2:00 PM",
        "12:45 PM", "3:30 PM"
    ],
    "Severity": [4, 5, 4, 3, 5, 3, 4, 4, 5, 3],
    "Description": [
        "Internet connection is slow",
        "Long queue during lunch",
        "Computers are working slowly",
        "Not enough seats available",
        "Wi-Fi becomes very slow",
        "Drinking water problem",
        "Queue becomes very long",
        "Computer takes time to respond",
        "Internet disconnects frequently",
        "Library seats are occupied"
    ]
}

if "reports" not in st.session_state:
    st.session_state.reports = pd.DataFrame(data)

df = st.session_state.reports

st.markdown(
    '<div class="main-title">Campus Problem Analysis</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Analysis of common college problems using student reports</div>',
    unsafe_allow_html=True
)

st.divider()

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Reports", len(df))
c2.metric("High Severity", len(df[df["Severity"] >= 4]))
c3.metric("Top Problem", df["Problem"].value_counts().idxmax())
c4.metric("Top Location", df["Location"].value_counts().idxmax())

st.markdown(
    '<div class="section-title">Explore Reports</div>',
    unsafe_allow_html=True
)

f1, f2 = st.columns(2)

with f1:
    selected_problem = st.selectbox(
        "Filter by Problem",
        ["All"] + sorted(df["Problem"].unique().tolist())
    )

with f2:
    selected_location = st.selectbox(
        "Filter by Location",
        ["All"] + sorted(df["Location"].unique().tolist())
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

st.markdown(
    '<div class="section-title">Problem Analysis</div>',
    unsafe_allow_html=True
)

result = []

for problem in df["Problem"].unique():

    values = df[df["Problem"] == problem]["Severity"]

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

st.markdown(
    '<div class="section-title">Problem-wise Reports</div>',
    unsafe_allow_html=True
)

st.bar_chart(df["Problem"].value_counts())

st.markdown(
    '<div class="section-title">Severity Analysis</div>',
    unsafe_allow_html=True
)

st.bar_chart(
    df["Severity"].value_counts().sort_index()
)

st.markdown(
    '<div class="section-title">Location-wise Reports</div>',
    unsafe_allow_html=True
)

st.bar_chart(df["Location"].value_counts())

st.markdown(
    '<div class="section-title">Problem Patterns</div>',
    unsafe_allow_html=True
)

patterns = (
    df.groupby(["Problem", "Location"])
    .size()
    .reset_index(name="Reports")
    .sort_values("Reports", ascending=False)
)

st.dataframe(
    patterns,
    use_container_width=True,
    hide_index=True
)

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

recommendations = {
    "Wi-Fi": "Wi-Fi should be checked in the areas where reports are frequent.",
    "Canteen Queue": "Queue management should be improved during busy hours.",
    "Slow Computer": "Lab computers should be checked and maintained regularly.",
    "No Seats": "Library seating should be increased during peak hours.",
    "Water Problem": "Drinking water facilities should be checked regularly.",
    "Electricity": "Electrical equipment and power usage should be checked.",
    "Noise": "The source of noise should be identified and managed."
}

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
    f"Current priority score: {prediction['Priority Score']}"
)

st.caption(
    "This prediction is based on the current report data. "
    "More real college data can improve future predictions."
)

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

severity = st.slider("Severity", 1, 5, 3)

description = st.text_area("Describe the problem")

if st.button("Submit Report"):

    if description.strip():

        new_report = pd.DataFrame([{
            "Problem": problem,
            "Location": location,
            "Time": time,
            "Severity": severity,
            "Description": description
        }])

        st.session_state.reports = pd.concat(
            [st.session_state.reports, new_report],
            ignore_index=True
        )

        st.success("Report submitted successfully.")
        st.rerun()

    else:
        st.warning("Please describe the problem.")