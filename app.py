import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# -------------------------------------------------
# PAGE SETTINGS
# -------------------------------------------------

st.set_page_config(
    page_title="Campus Problem Analysis",
    page_icon="📊",
    layout="wide"
)


# -------------------------------------------------
# GOOGLE SHEETS
# -------------------------------------------------

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


# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------

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

    df["Problem"] = df["Problem"].astype(str).str.strip()
    df["Location"] = df["Location"].astype(str).str.strip()
    df["Time"] = df["Time"].astype(str).str.strip()


# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------

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


# -------------------------------------------------
# FILTERS
# -------------------------------------------------

if not df.empty:

    st.sidebar.subheader("🔎 Filters")

    problem_options = sorted(
        df["Problem"].unique().tolist()
    )

    selected_problem = st.sidebar.multiselect(
        "Problem",
        problem_options,
        default=problem_options
    )


    location_options = sorted(
        df["Location"].unique().tolist()
    )

    selected_location = st.sidebar.multiselect(
        "Location",
        location_options,
        default=location_options
    )


    severity_range = st.sidebar.slider(
        "Severity",
        min_value=1,
        max_value=5,
        value=(1, 5)
    )


    filtered_df = df[
        df["Problem"].isin(selected_problem)
        &
        df["Location"].isin(selected_location)
        &
        df["Severity"].between(
            severity_range[0],
            severity_range[1]
        )
    ]

else:

    filtered_df = df.copy()


# =================================================
# DASHBOARD
# =================================================

if page == "🏠 Dashboard":

    st.title("Campus Problem Analysis")

    st.write(
        "Interactive analysis of common problems "
        "reported by students."
    )

    st.divider()


    if df.empty:

        st.info(
            "No reports available yet."
        )

    elif filtered_df.empty:

        st.warning(
            "No reports match the selected filters."
        )

    else:

        # -----------------------------------------
        # METRICS
        # -----------------------------------------

        total_reports = len(filtered_df)

        high_severity = len(
            filtered_df[
                filtered_df["Severity"] >= 4
            ]
        )

        average_severity = round(
            filtered_df["Severity"].mean(),
            2
        )

        top_problem = (
            filtered_df["Problem"]
            .value_counts()
            .idxmax()
        )


        c1, c2, c3, c4 = st.columns(4)


        c1.metric(
            "📋 Total Reports",
            total_reports
        )

        c2.metric(
            "⚠️ High Severity",
            high_severity
        )

        c3.metric(
            "📊 Average Severity",
            f"{average_severity}/5"
        )

        c4.metric(
            "🚨 Top Problem",
            top_problem
        )


        st.divider()


        # -----------------------------------------
        # PROBLEM FREQUENCY
        # -----------------------------------------

        st.subheader("📌 Problem Frequency")

        problem_count = (
            filtered_df["Problem"]
            .value_counts()
            .sort_values(ascending=True)
        )

        st.bar_chart(
            problem_count,
            horizontal=True
        )


        # -----------------------------------------
        # TWO GRAPHS
        # -----------------------------------------

        left, right = st.columns(2)


        with left:

            st.subheader(
                "⚠️ Severity Distribution"
            )

            severity_count = (
                filtered_df["Severity"]
                .value_counts()
                .sort_index()
            )

            st.bar_chart(
                severity_count
            )


        with right:

            st.subheader(
                "📍 Reports by Location"
            )

            location_count = (
                filtered_df["Location"]
                .value_counts()
            )

            st.bar_chart(
                location_count
            )


        st.divider()


        # -----------------------------------------
        # TIME PATTERN
        # -----------------------------------------

        st.subheader(
            "⏰ Reporting Time Pattern"
        )

        time_count = (
            filtered_df["Time"]
            .value_counts()
        )

        st.bar_chart(
            time_count
        )


# =================================================
# ANALYSIS
# =================================================

elif page == "📊 Analysis":

    st.title("📊 Detailed Analysis")

    if df.empty:

        st.info(
            "No reports available."
        )

    elif filtered_df.empty:

        st.warning(
            "No reports match the selected filters."
        )

    else:

        # -----------------------------------------
        # PRIORITY SCORE
        # -----------------------------------------

        st.subheader(
            "🎯 Problem Priority Ranking"
        )

        priority_rows = []


        for problem in filtered_df[
            "Problem"
        ].unique():

            problem_data = filtered_df[
                filtered_df["Problem"] == problem
            ]

            reports = len(problem_data)

            avg_severity = problem_data[
                "Severity"
            ].mean()

            priority_score = (
                reports * avg_severity
            )


            if priority_score >= 15:

                level = "Critical"

            elif priority_score >= 10:

                level = "High"

            elif priority_score >= 5:

                level = "Medium"

            else:

                level = "Low"


            priority_rows.append({

                "Problem": problem,

                "Reports": reports,

                "Average Severity": round(
                    avg_severity,
                    2
                ),

                "Priority Score": round(
                    priority_score,
                    2
                ),

                "Priority Level": level
            })


        priority_df = pd.DataFrame(
            priority_rows
        )


        priority_df = priority_df.sort_values(
            "Priority Score",
            ascending=False
        )


        st.dataframe(
            priority_df,
            use_container_width=True,
            hide_index=True
        )


        st.divider()


        # -----------------------------------------
        # PROBLEM × LOCATION
        # -----------------------------------------

        st.subheader(
            "📍 Problem × Location"
        )


        problem_location = pd.crosstab(
            filtered_df["Problem"],
            filtered_df["Location"]
        )


        st.dataframe(
            problem_location,
            use_container_width=True
        )


        st.divider()


        # -----------------------------------------
        # TIME ANALYSIS
        # -----------------------------------------

        st.subheader(
            "⏰ Time Analysis"
        )


        time_count = (
            filtered_df["Time"]
            .value_counts()
        )


        st.bar_chart(
            time_count
        )


        peak_time = time_count.idxmax()


        st.info(
            f"Most reports are associated with "
            f"**{peak_time}**."
        )


        st.divider()


        # -----------------------------------------
        # LOCATION ANALYSIS
        # -----------------------------------------

        st.subheader(
            "📍 Location Analysis"
        )


        location_analysis = (
            filtered_df
            .groupby("Location")
            .agg(
                Reports=("Problem", "count"),
                Average_Severity=(
                    "Severity",
                    "mean"
                )
            )
            .reset_index()
        )


        location_analysis[
            "Average_Severity"
        ] = (
            location_analysis[
                "Average_Severity"
            ]
            .round(2)
        )


        location_analysis = (
            location_analysis
            .sort_values(
                "Reports",
                ascending=False
            )
        )


        st.dataframe(
            location_analysis,
            use_container_width=True,
            hide_index=True
        )


        st.divider()


        # -----------------------------------------
        # DOWNLOAD
        # -----------------------------------------

        st.download_button(
            "📥 Download Filtered Analysis",
            priority_df.to_csv(
                index=False
            ),
            "campus_filtered_analysis.csv",
            "text/csv"
        )


# =================================================
# REPORT PROBLEM
# =================================================

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
        placeholder=(
            "Example: Wi-Fi becomes slow "
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
                "✅ Report submitted successfully!"
            )

            st.rerun()

        else:

            st.warning(
                "Please describe the problem."
            )


# =================================================
# INSIGHTS
# =================================================

elif page == "💡 Insights":

    st.title("💡 Smart Insights")


    if df.empty:

        st.info(
            "Add reports to generate insights."
        )

    elif filtered_df.empty:

        st.warning(
            "No reports match the selected filters."
        )

    else:

        problem_count = (
            filtered_df["Problem"]
            .value_counts()
        )

        location_count = (
            filtered_df["Location"]
            .value_counts()
        )

        time_count = (
            filtered_df["Time"]
            .value_counts()
        )


        top_problem = problem_count.idxmax()

        top_location = location_count.idxmax()

        peak_time = time_count.idxmax()

        high_severity = len(
            filtered_df[
                filtered_df["Severity"] >= 4
            ]
        )


        # -----------------------------------------
        # INSIGHTS
        # -----------------------------------------

        st.subheader(
            "🚨 Most Reported Problem"
        )

        st.success(
            f"**{top_problem}** is the most "
            f"frequently reported problem."
        )


        st.subheader(
            "📍 Problem Hotspot"
        )

        st.info(
            f"**{top_location}** has the highest "
            f"number of reports."
        )


        st.subheader(
            "⏰ Peak Reporting Time"
        )

        st.warning(
            f"Most reports are associated with "
            f"**{peak_time}**."
        )


        st.subheader(
            "⚠️ Severity Alert"
        )


        if high_severity > 0:

            st.error(
                f"There are **{high_severity}** "
                f"high-severity reports."
            )

        else:

            st.success(
                "No high-severity reports currently."
            )


        # -----------------------------------------
        # RECOMMENDATION
        # -----------------------------------------

        st.subheader(
            "💡 Recommended Action"
        )


        recommendations = {

            "Wi-Fi":
                "Check network performance in frequently affected areas and during peak hours.",

            "Canteen Queue":
                "Improve queue management during busy hours.",

            "Slow Computer":
                "Inspect and maintain computers in frequently affected labs.",

            "No Seats":
                "Analyze peak library usage and consider additional seating.",

            "Water Problem":
                "Regularly inspect drinking-water facilities.",

            "Electricity":
                "Inspect electrical equipment and power supply.",

            "Noise":
                "Identify and control major sources of noise.",

            "Other":
                "Investigate the most frequently reported problem."
        }


        st.info(
            recommendations.get(
                top_problem,
                "Investigate the most frequently reported problem."
            )
        )


        st.caption(
            "Insights are generated from the "
            "currently available reports."
        )


# -------------------------------------------------
# FOOTER
# -------------------------------------------------

st.divider()

st.caption(
    "Campus Problem Analysis • "
    "Student Data Science Project"
)