import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Campus Problem Analysis",
    page_icon="📊",
    layout="wide"
)

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

st.title("Campus Problem Analysis")
st.caption("Analysis of common college problems using student reports")

st.divider()

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Reports", len(df))
c2.metric("High Severity", len(df[df["Severity"] >= 4]))
c3.metric("Top Problem", df["Problem"].value_counts().idxmax())
c4.metric("Top Location", df["Location"].value_counts().idxmax())

st.divider()

st.subheader("Explore Reports")

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

st.subheader("Problem Analysis")

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

st.subheader("Problem-wise Reports")
st.bar_chart(df["Problem"].value_counts())

st.subheader("Severity Analysis")
st.bar_chart(df["Severity"].value_counts().sort_index())

st.subheader("Location-wise Reports")
st.bar_chart(df["Location"].value_counts())

top_problem = analysis.iloc[0]["Problem"]
top_location = df[
    df["Problem"] == top_problem
]["Location"].value_counts().idxmax()

st.subheader("Smart Insight")

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

st.subheader("Recommendation")

st.info(
    recommendations.get(
        top_problem,
        "The highest priority problem needs attention."
    )
)

st.subheader("Report a Problem")

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

severity = st.slider("Severity", 1, 5, 3)

description = st.text_area("Describe the problem")

if st.button("Submit Report"):

    if description.strip():

        new_report = pd.DataFrame([{
            "Problem": problem,
            "Location": location,
            "Time": "Not specified",
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