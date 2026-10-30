
import sys
from pathlib import Path

import streamlit as st
import plotly.express as px

# Allow imports from the project root
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

# Ensure module updates in src are reloaded during hot reloads
import importlib
if "src.consumption" in sys.modules:
    importlib.reload(sys.modules["src.consumption"])

from src.data_loader import load_electricity_data
from src.data_cleaner import clean_electricity_data

from src.consumption import (
    calculate_energy,
    get_daily_consumption,
    get_hourly_consumption,
    get_monthly_consumption,
    get_average_daily_consumption,
    get_highest_consumption_day,
    get_lowest_consumption_day,
    get_peak_usage_hour,
    generate_consumption_summary
)

DATA_PATH = ROOT_DIR / "data" / "household_power_consumption.txt"


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="ElectWatch",
    page_icon="⚡",
    layout="wide"
)


# --------------------------------------------------
# Theme selection
# --------------------------------------------------

if "theme" not in st.session_state:
    st.session_state.theme = "Light"

theme = st.sidebar.selectbox(
    "Appearance",
    ["Light", "Dark"],
    index=0,
    key="theme"
)

if theme == "Light":
    background = "#FFFFFF"
    text_color = "#202B3C"
    sidebar_background = "#F5F7FB"
    chart_template = "plotly_white"
else:
    background = "#111827"
    text_color = "#F9FAFB"
    sidebar_background = "#1F2937"
    chart_template = "plotly_dark"


st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {background};
        color: {text_color};
    }}

    [data-testid="stSidebar"] {{
        background-color: {sidebar_background};
    }}

    h1, h2, h3, h4, h5, p, label, li {{
        color: {text_color};
    }}
    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# Load and prepare data
# --------------------------------------------------

@st.cache_data
def prepare_data():

    raw_data = load_electricity_data(str(DATA_PATH))

    cleaned_data = clean_electricity_data(raw_data)

    energy_data = calculate_energy(cleaned_data)

    daily = get_daily_consumption(energy_data)
    hourly = get_hourly_consumption(energy_data)
    monthly = get_monthly_consumption(energy_data)

    average = get_average_daily_consumption(energy_data)

    total = energy_data["energy_kwh"].sum()

    return energy_data, daily, hourly, monthly, average, total


try:
    (
        energy_data,
        daily,
        hourly,
        monthly,
        average,
        total
    ) = prepare_data()

except Exception as error:
    st.error(f"Unable to load electricity data: {error}")
    st.stop()


# --------------------------------------------------
# Sidebar navigation
# --------------------------------------------------

st.sidebar.title("⚡ ElectWatch")

st.sidebar.caption("Household Electricity Analytics")

page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Daily Analysis",
        "Monthly Analysis",
        "Hourly Analysis"
    ]
)

st.sidebar.divider()

st.sidebar.caption("Dataset: UCI Household Power Consumption")

st.sidebar.caption("Data period: 2006–2010")

# --------------------------------------------------
# Date range filtering
# --------------------------------------------------

st.sidebar.divider()

st.sidebar.subheader("Filter Consumption Period")

min_date = energy_data["datetime"].min().date()
max_date = energy_data["datetime"].max().date()

selected_dates = st.sidebar.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if len(selected_dates) == 2:

    start_date, end_date = selected_dates

    if end_date is None:
        end_date = start_date

else:
    start_date = selected_dates[0]
    end_date = selected_dates[0]


# Filter readings
filtered_data = energy_data[
    (energy_data["datetime"].dt.date >= start_date) &
    (energy_data["datetime"].dt.date <= end_date)
].copy()


# Stop if selected period has no readings
if filtered_data.empty:
    st.warning("No electricity readings found for this date range.")
    st.stop()


# Recalculate consumption for selected period
daily = get_daily_consumption(filtered_data)

hourly = get_hourly_consumption(filtered_data)

monthly = get_monthly_consumption(filtered_data)

average = get_average_daily_consumption(filtered_data)

total = filtered_data["energy_kwh"].sum()


# --------------------------------------------------
# Overview page
# --------------------------------------------------

if page == "Overview":

    st.title("Electricity Consumption Overview")

    st.write(
        "Understand household electricity usage "
        "through interactive data analytics."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Consumption",
            f"{total:,.2f} kWh"
        )

    with col2:
        st.metric(
            "Average Daily Consumption",
            f"{average:.2f} kWh"
        )

    with col3:
        st.metric(
            "Total Readings",
            f"{len(energy_data):,}"
        )
    
    st.download_button(
        label="Download Consumption Data (CSV)",
        data=filtered_data.to_csv(index=False).encode("utf-8"),
        file_name="electwatch_consumption.csv",
        mime="text/csv"
    )


    st.divider()

    st.subheader("Consumption Insights")

    highest_day = get_highest_consumption_day(daily)
    lowest_day = get_lowest_consumption_day(filtered_data, daily_data=daily)
    peak_hour = get_peak_usage_hour(hourly)
    summary_text = generate_consumption_summary(highest_day, lowest_day, peak_hour)

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.metric(
            "Highest Consumption Day",
            f"{highest_day['consumption_kwh']:,.2f} kWh"
        )
        st.caption(f"📅 **Date:** {highest_day['date']}")

    with col_b:
        st.metric(
            "Lowest Consumption Day",
            f"{lowest_day['consumption_kwh']:,.2f} kWh"
        )
        lowest_note = " *(partial day)*" if not lowest_day.get("is_complete", True) else ""
        st.caption(f"📅 **Date:** {lowest_day['date']}{lowest_note}")

    with col_c:
        st.metric(
            "Peak Usage Hour",
            peak_hour["hour_label"]
        )
        st.caption(f"⚡ **Average:** {peak_hour['consumption_kwh']:.2f} kWh")

    st.markdown("##### Automatic Consumption Summary")
    st.markdown(summary_text)

    st.divider()

    st.subheader("Daily Electricity Consumption")

    fig = px.line(
        daily,
        x="date",
        y="consumption_kwh",
        labels={
            "date": "Date",
            "consumption_kwh": "Consumption (kWh)"
        }
    )

    fig.update_layout(template=chart_template)

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Monthly Electricity Consumption")

    fig = px.bar(
        monthly,
        x="month",
        y="consumption_kwh",
        labels={
            "month": "Month",
            "consumption_kwh": "Consumption (kWh)"
        }
    )

    fig.update_layout(template=chart_template)

    st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------
# Daily analysis
# --------------------------------------------------

elif page == "Daily Analysis":

    st.title("Daily Consumption Analysis")

    st.write("Explore electricity consumption across individual days.")

    fig = px.line(
        daily,
        x="date",
        y="consumption_kwh",
        labels={
            "date": "Date",
            "consumption_kwh": "Consumption (kWh)"
        }
    )

    fig.update_layout(template=chart_template)

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Daily Consumption Records")

    st.dataframe(
        daily,
        use_container_width=True,
        hide_index=True
    )


# --------------------------------------------------
# Monthly analysis
# --------------------------------------------------

elif page == "Monthly Analysis":

    st.title("Monthly Consumption Analysis")

    st.write("Compare electricity consumption month by month.")

    fig = px.bar(
        monthly,
        x="month",
        y="consumption_kwh",
        labels={
            "month": "Month",
            "consumption_kwh": "Consumption (kWh)"
        }
    )

    fig.update_layout(template=chart_template)

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Monthly Consumption Records")

    st.dataframe(
        monthly,
        use_container_width=True,
        hide_index=True
    )


# --------------------------------------------------
# Hourly analysis
# --------------------------------------------------

elif page == "Hourly Analysis":

    st.title("Hourly Consumption Analysis")

    st.write(
        "Understand how electricity consumption "
        "changes throughout the day."
    )

    hourly_data = hourly.copy()

    hourly_data["hour"] = hourly_data["datetime"].dt.hour

    average_hourly = (
        hourly_data.groupby("hour")["consumption_kwh"]
        .mean()
        .reset_index()
    )

    fig = px.line(
        average_hourly,
        x="hour",
        y="consumption_kwh",
        markers=True,
        labels={
            "hour": "Hour of Day",
            "consumption_kwh": "Average Consumption (kWh)"
        }
    )

    fig.update_xaxes(
        tickmode="linear",
        tick0=0,
        dtick=1,
        range=[0, 23]
    )

    fig.update_layout(template=chart_template)

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Hourly Consumption Records")

    st.dataframe(
        average_hourly,
        use_container_width=True,
        hide_index=True
    )
