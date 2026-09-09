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

    required_columns = [
        "Problem",
        "Location",
        "Time",
        "Severity",
        "Description",
        "Date"
    ]

    for col in required_columns:
        if col not in df.columns:
            df[col] = ""

    df = df[required_columns]

    df["Severity"] = pd.to_numeric(
        df["Severity"],
        errors="coerce"
    )

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
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

# ---------------- SIDEBAR ----------------

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

# ---------------- FILTERS ----------------

filtered_df = df.copy()

if not df.empty:

    st.sidebar.markdown("---")
    st.sidebar.subheader("🔎 Filters")

    problem_options = sorted(
        df["Problem"].dropna().unique().tolist()
    )

    location_options = sorted(
        df["Location"].dropna().unique().tolist()
    )

    selected_problems = st.sidebar.multiselect(
        "Problem",
        problem_options
    )

    selected_locations = st.sidebar.multiselect(
        "Location",
        location_options
    )

    severity_range = st.sidebar.slider(
        "Severity",
        min_value=1,
        max_value=5,
        value=(1, 5)
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
        st.warning("No reports match the selected filters.")
        st.stop()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📌 Problem Frequency")

        problem_counts = (
            filtered_df["Problem"]
            .value_counts()
            .sort_values()
        )

        st.bar_chart(problem_counts)

    with col2:
        st.subheader("⚠️ Severity Distribution")

        severity_counts = (
            filtered_df["Severity"]
            .value_counts()
            .sort_index()
        )

        st.bar_chart(severity_counts)

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

    # -------- NEW TREND ANALYSIS --------

    st.markdown("---")
    st.subheader("📈 Problem Trend")

    trend_df = filtered_df.dropna(subset=["Date"]).copy()

    if not trend_df.empty:

        trend_df["Date"] = pd.to_datetime(
            trend_df["Date"]
        ).dt.date

        daily_reports = (
            trend_df.groupby("Date")
            .size()
            .rename("Reports")
        )

        st.line_chart(daily_reports)

        st.caption(
            "Shows how the number of reported problems changes over time."
        )

    else:
        st.info(
            "Trend analysis will appear when reports have dates."
        )


# ---------------- ANALYSIS ----------------

elif page == "📊 Analysis":

    st.title("📊 Detailed Analysis")

    if filtered_df.empty:
        st.warning("No data available for the selected filters.")
        st.stop()

    # Priority Score

    st.subheader("🎯 Priority Analysis")

    priority = (
        filtered_df.groupby("Problem")
        .agg(
            Reports=("Problem", "count"),
            Average_Severity=("Severity", "mean")
        )
    )

    priority["Priority Score"] = (
        priority["Reports"] *
        priority["Average_Severity"]
    )

    priority = priority.sort_values(
        "Priority Score",
        ascending=False
    )

    st.dataframe(
        priority.round(2),
        use_container_width=True
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

    # Time Analysis

    st.subheader("🕐 Time Analysis")

    time_analysis = (
        filtered_df["Time"]
        .value_counts()
        .rename_axis("Time")
        .reset_index(name="Reports")
    )

    st.bar_chart(
        time_analysis.set_index("Time")
    )

    # Location Analysis

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

    # -------- NEW TREND ANALYSIS --------

    st.subheader("📈 Reports Over Time")

    trend_df = filtered_df.dropna(
        subset=["Date"]
    ).copy()

    if not trend_df.empty:

        trend_df["Date"] = pd.to_datetime(
            trend_df["Date"]
        ).dt.date

        daily_trend = (
            trend_df.groupby("Date")
            .size()
            .rename("Reports")
        )

        st.line_chart(daily_trend)

        # Weekly trend

        weekly_df = trend_df.copy()

        weekly_df["Week"] = (
            pd.to_datetime(
                weekly_df["Date"]
            ).dt.to_period("W")
            .astype(str)
        )

        weekly_trend = (
            weekly_df.groupby("Week")
            .size()
            .rename("Reports")
        )

        st.subheader("📅 Weekly Trend")

        st.bar_chart(weekly_trend)

    else:
        st.info(
            "Add dated reports to see time trends."
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


# ---------------- REPORT PROBLEM ----------------

elif page == "📝 Report Problem":

    st.title("📝 Report a Campus Problem")

    st.write(
        "Submit a problem anonymously. "
        "Your report will be added to the campus dataset."
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
        min_value=1,
        max_value=5,
        value=3
    )

    description = st.text_area(
        "Description",
        placeholder="Describe the problem..."
    )

    report_date = date.today().strftime(
        "%Y-%m-%d"
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
        st.warning("No data available for the selected filters.")
        st.stop()

    top_problem = (
        filtered_df["Problem"]
        .value_counts()
        .idxmax()
    )

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

    high_severity = (
        filtered_df["Severity"]
        .mean()
    )

    st.subheader("📌 Key Findings")

    st.write(
        f"• Most reported problem: **{top_problem}**"
    )

    st.write(
        f"• Most affected location: **{top_location}**"
    )

    st.write(
        f"• Most common reporting time: **{peak_time}**"
    )

    st.write(
        f"• Average severity: **{high_severity:.1f}/5**"
    )

    st.markdown("---")

    st.subheader("💡 Recommended Actions")

    recommendations = {
        "Wi-Fi":
            "IT team should check network connectivity and access points.",
        "Canteen":
            "Consider improving queue management during peak hours.",
        "Lab PC":
            "Technical team should inspect slow or faulty systems.",
        "Library":
            "Review seating availability and resource access.",
        "Water":
            "Facilities team should inspect water supply points.",
        "Electricity":
            "Maintenance team should check electrical infrastructure.",
        "Cleanliness":
            "Cleaning frequency may need to be increased."
    }

    if top_problem in recommendations:
        st.info(
            recommendations[top_problem]
        )
    else:
        st.info(
            "The administration should review the reported issue and "
            "identify an appropriate solution."
        )

    st.markdown("---")

    st.caption(
        "Note: Current insights are based on submitted reports "
        "and priority analysis. They are not ML predictions."
    )


# ---------------- FOOTER ----------------

st.markdown("---")

st.caption(
    "Campus Problem Analysis • Student Project"
)