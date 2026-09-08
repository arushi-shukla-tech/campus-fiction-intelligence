import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Campus Friction Intelligence",
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
    "Severity": [4, 5, 4, 3, 5, 3, 4, 4, 5, 3]
}

if "reports" not in st.session_state:
    st.session_state.reports = pd.DataFrame(data)

df = st.session_state.reports

st.title("Campus Friction Intelligence")
st.caption("College problem analysis using student reports")

total = len(df)
high = len(df[df["Severity"] >= 4])
top_problem = df["Problem"].value_counts().idxmax()
top_location = df["Location"].value_counts().idxmax()

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Reports", total)
c2.metric("High Severity", high)
c3.metric("Top Problem", top_problem)
c4.metric("Top Location", top_location)

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

recommendations = {
    "Wi-Fi": "Wi-Fi should be checked in the affected areas.",
    "Canteen Queue": "Queue management should be improved during busy hours.",
    "Slow Computer": "Lab computers should be checked and maintained.",
    "No Seats": "Library seating should be increased during busy hours.",
    "Water Problem": "Drinking water facilities should be checked.",
    "Electricity": "Electrical equipment should be checked in the affected area.",
    "Noise": "The source of noise should be identified and managed."
}

st.subheader("Recommendation")

st.info(
    recommendations.get(
        top_problem,
        "The problem with the highest priority needs attention."
    )
)

st.subheader("Report a Problem")

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

description = st.text_area("Description")

if st.button("Submit"):

    if description.strip():

        new_report = pd.DataFrame([{
            "Problem": problem,
            "Location": location,
            "Time": "Not specified",
            "Severity": severity
        }])

        st.session_state.reports = pd.concat(
            [st.session_state.reports, new_report],
            ignore_index=True
        )

        st.success("Report submitted successfully.")
        st.rerun()

    else:
        st.warning("Please enter a description.")