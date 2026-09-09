import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

st.set_page_config(
    page_title="Campus Problem Analysis",
    page_icon="🎓",
    layout="wide"
)

# Google Sheets
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


def load_data():
    records = sheet.get_all_records()

    if not records:
        return pd.DataFrame(
            columns=[
                "Problem",
                "Location",
                "Time",
                "Severity",
                "Description",
                "Date"
            ]
        )

    df = pd.DataFrame(records)

    columns = [
        "Problem",
        "Location",
        "Time",
        "Severity",
        "Description",
        "Date"
    ]

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

    df["Problem"] = df["Problem"].astype(str).str.strip()
    df["Location"] = df["Location"].astype(str).str.strip()
    df["Time"] = df["Time"].astype(str).str.strip()
    df["Description"] = df["Description"].astype(str).str.strip()

    return df


df = load_data()

# Sidebar
st.sidebar.title("🎓 Campus Problem Analysis")

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "📊 Analysis",
        "📝 Report Problem",
        "💡 Insights"
    ]
)

# Filters
filtered_df = df.copy()

if not df.empty:

    st.sidebar.markdown("---")
    st.sidebar.subheader("🔎 Filters")

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
            filtered_df["Problem"].isin(selected_problems)
        ]

    if selected_locations:
        filtered_df = filtered_df[
            filtered_df["Location"].isin(selected_locations)
        ]

    filtered_df = filtered_df[
        filtered_df["Severity"].between(
            severity_range[0],
            severity_range[1]
        )
    ]


# Priority function
def get_priority(score):

    if score >= 16:
        return "🔴 Critical"

    elif score >= 11:
        return "🟠 High"

    elif score >= 6:
        return "🟡 Medium"

    else:
        return "🟢 Low"


# ---------------- DASHBOARD ----------------

if page == "🏠 Dashboard":

    st.title("🎓 Campus Problem Analysis")

    st.caption(
        "Analysis of common college problems using student reports"
    )

    if df.empty:
        st.info("No reports available yet.")
        st.stop()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Reports",
        len(filtered_df)
    )

    col2.metric(
        "Average Severity",
        round(filtered_df["Severity"].mean(), 1)
        if not filtered_df.empty else 0
    )

    col3.metric(
        "Most Reported Problem",
        filtered_df["Problem"].value_counts().idxmax()
        if not filtered_df.empty else "-"
    )

    col4.metric(
        "Locations",
        filtered_df["Location"].nunique()
    )

    st.markdown("---")

    if filtered_df.empty:
        st.warning(
            "No reports match the selected filters."
        )
        st.stop()

    # Priority overview
    st.subheader("🚨 Priority Overview")

    priority_data = (
        filtered_df.groupby("Problem")
        .agg(
            Reports=("Problem", "count"),
            Average_Severity=("Severity", "mean")
        )
    )

    priority_data["Frequency Score"] = (
        priority_data["Reports"] /
        priority_data["Reports"].max()
    ) * 10

    priority_data["Severity Score"] = (
        priority_data["Average_Severity"] / 5
    ) * 10

    priority_data["Priority Score"] = (
        priority_data["Frequency Score"] * 0.5
        + priority_data["Severity Score"] * 0.5
    )

    priority_data["Priority"] = (
        priority_data["Priority Score"]
        .apply(get_priority)
    )

    priority_data = priority_data.sort_values(
        "Priority Score",
        ascending=False
    )

    st.dataframe(
        priority_data[
            [
                "Reports",
                "Average_Severity",
                "Priority Score",
                "Priority"
            ]
        ].round(2),
        use_container_width=True
    )

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📌 Problem Frequency")

        counts = (
            filtered_df["Problem"]
            .value_counts()
            .sort_values()
        )

        st.bar_chart(counts)

    with col2:
        st.subheader("⚠️ Severity Distribution")

        severity = (
            filtered_df["Severity"]
            .value_counts()
            .sort_index()
        )

        st.bar_chart(severity)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📍 Reports by Location")

        location_counts = (
            filtered_df["Location"]
            .value_counts()
            .sort_values()
        )

        st.bar_chart(location_counts)

    with col2:
        st.subheader("🕐 Time Pattern")

        time_counts = (
            filtered_df["Time"]
            .value_counts()
        )

        st.bar_chart(time_counts)

    # Trend
    st.markdown("---")
    st.subheader("📈 Problem Trend")

    trend_df = filtered_df.dropna(
        subset=["Date"]
    ).copy()

    if not trend_df.empty:

        trend_df["Date"] = pd.to_datetime(
            trend_df["Date"]
        ).dt.date

        daily = (
            trend_df.groupby("Date")
            .size()
            .rename("Reports")
        )

        st.line_chart(daily)

    else:
        st.info(
            "Trend will appear when reports have valid dates."
        )


# ---------------- ANALYSIS ----------------

elif page == "📊 Analysis":

    st.title("📊 Detailed Analysis")

    if filtered_df.empty:
        st.warning("No data available.")
        st.stop()

    # Priority analysis
    st.subheader("🚨 Smart Priority Analysis")

    priority = (
        filtered_df.groupby("Problem")
        .agg(
            Reports=("Problem", "count"),
            Average_Severity=("Severity", "mean")
        )
    )

    priority["Frequency Score"] = (
        priority["Reports"] /
        priority["Reports"].max()
    ) * 10

    priority["Severity Score"] = (
        priority["Average_Severity"] / 5
    ) * 10

    priority["Priority Score"] = (
        priority["Frequency Score"] * 0.5
        + priority["Severity Score"] * 0.5
    )

    priority["Priority"] = (
        priority["Priority Score"]
        .apply(get_priority)
    )

    priority = priority.sort_values(
        "Priority Score",
        ascending=False
    )

    st.dataframe(
        priority.round(2),
        use_container_width=True
    )

    # Highest priority
    highest = priority.iloc[0]

    st.success(
        f"🚨 Highest priority problem: "
        f"**{priority.index[0]}** "
        f"({highest['Priority']})"
    )

    # Problem x Location
    st.subheader("📍 Problem × Location")

    problem_location = pd.crosstab(
        filtered_df["Problem"],
        filtered_df["Location"]
    )

    st.dataframe(
        problem_location,
        use_container_width=True
    )

    # Location analysis
    st.subheader("📍 Location Analysis")

    location_analysis = (
        filtered_df.groupby("Location")
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

    # Time analysis
    st.subheader("🕐 Time Analysis")

    time_analysis = (
        filtered_df["Time"]
        .value_counts()
    )

    st.bar_chart(time_analysis)

    # Trend
    st.subheader("📈 Reports Over Time")

    trend = filtered_df.dropna(
        subset=["Date"]
    ).copy()

    if not trend.empty:

        trend["Date"] = pd.to_datetime(
            trend["Date"]
        ).dt.date

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

    csv = filtered_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "⬇️ Download Filtered Data",
        csv,
        "campus_reports.csv",
        "text/csv"
    )


# ---------------- REPORT PROBLEM ----------------

elif page == "📝 Report Problem":

    st.title("📝 Report a Campus Problem")

    st.write(
        "Submit a problem anonymously."
    )

    problem = st.selectbox(
        "Problem",
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

    location = st.selectbox(
        "Location",
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
        "Time",
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
        "Severity",
        1,
        5,
        3
    )

    description = st.text_area(
        "Description",
        placeholder="Describe the problem..."
    )

    report_date = date.today().strftime(
        "%d-%m-%Y"
    )

    st.caption(
        f"Report Date: {report_date}"
    )

    if st.button("Submit Report"):

        if description.strip() == "":
            st.warning(
                "Please enter a description."
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
                "Your report has been submitted successfully! ✅"
            )

            st.rerun()


# ---------------- INSIGHTS ----------------

elif page == "💡 Insights":

    st.title("💡 Smart Insights")

    if filtered_df.empty:
        st.warning("No data available.")
        st.stop()

    # Priority calculation
    priority = (
        filtered_df.groupby("Problem")
        .agg(
            Reports=("Problem", "count"),
            Average_Severity=("Severity", "mean")
        )
    )

    priority["Frequency Score"] = (
        priority["Reports"] /
        priority["Reports"].max()
    ) * 10

    priority["Severity Score"] = (
        priority["Average_Severity"] / 5
    ) * 10

    priority["Priority Score"] = (
        priority["Frequency Score"] * 0.5
        + priority["Severity Score"] * 0.5
    )

    priority["Priority"] = (
        priority["Priority Score"]
        .apply(get_priority)
    )

    priority = priority.sort_values(
        "Priority Score",
        ascending=False
    )

    top_problem = priority.index[0]
    top_priority = priority.iloc[0]["Priority"]

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

    st.subheader("🚨 Problems Needing Attention")

    st.info(
        f"**{top_problem}** currently has the highest priority: "
        f"**{top_priority}**."
    )

    st.write(
        f"📍 Most affected location: **{top_location}**"
    )

    st.write(
        f"🕐 Most common reporting time: **{peak_time}**"
    )

    st.write(
        f"📊 Average severity: "
        f"**{filtered_df['Severity'].mean():.1f}/5**"
    )

    st.markdown("---")

    st.subheader("💡 Recommended Action")

    recommendations = {
        "Wi-Fi":
            "IT team should check network connectivity and access points.",
        "Canteen":
            "Queue management and service capacity should be reviewed.",
        "Lab PC":
            "Technical team should inspect slow or faulty computers.",
        "Library":
            "Seating availability and library resources should be reviewed.",
        "Water":
            "Facilities team should inspect water supply points.",
        "Electricity":
            "Maintenance team should inspect electrical infrastructure.",
        "Cleanliness":
            "Cleaning frequency should be reviewed."
    }

    if top_problem in recommendations:
        st.success(
            recommendations[top_problem]
        )
    else:
        st.success(
            "Administration should review this problem "
            "and identify an appropriate solution."
        )

    st.markdown("---")

    st.caption(
        "Priority is calculated using report frequency "
        "and average severity. It is an analytical scoring system, "
        "not an ML prediction."
    )


# Footer
st.markdown("---")

st.caption(
    "Campus Problem Analysis • Student Project"
)