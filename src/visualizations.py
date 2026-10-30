
import plotly.express as px
import pandas as pd


def plot_daily_consumption(daily_data: pd.DataFrame):
    """Display daily electricity consumption."""

    fig = px.line(
        daily_data,
        x="date",
        y="consumption_kwh",
        title="Daily Electricity Consumption",
        labels={
            "date": "Date",
            "consumption_kwh": "Consumption (kWh)"
        }
    )

    fig.update_layout(hovermode="x unified")

    return fig


def plot_monthly_consumption(monthly_data: pd.DataFrame):
    """Compare electricity consumption across months."""

    fig = px.bar(
        monthly_data,
        x="month",
        y="consumption_kwh",
        title="Monthly Electricity Consumption",
        labels={
            "month": "Month",
            "consumption_kwh": "Consumption (kWh)"
        }
    )

    return fig


def plot_hourly_consumption(hourly_data: pd.DataFrame):
    """Display average electricity consumption by hour of day."""

    hourly_data = hourly_data.copy()

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
        title="Average Hourly Electricity Consumption",
        labels={
            "hour": "Hour of Day",
            "consumption_kwh": "Average Consumption (kWh)"
        }
    )

    fig.update_xaxes(
        tickmode="linear",
        tick0=0,
        dtick=1
    )

    return fig
