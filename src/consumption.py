
import pandas as pd


class InsightResult(dict):
    """
    A dictionary subclass supporting both dictionary key indexing
    and attribute access for insight result records.
    """
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"'InsightResult' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        self[name] = value


def calculate_energy(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate energy consumed for each one-minute reading.

    Global_active_power is measured in kW.
    Energy for one minute = Power / 60.
    """
    if data is None or data.empty:
        return pd.DataFrame(columns=["datetime", "Global_active_power", "energy_kwh"])

    result = data.copy()

    if "Global_active_power" in result.columns:
        result["Global_active_power"] = pd.to_numeric(result["Global_active_power"], errors="coerce")
        result["energy_kwh"] = result["Global_active_power"] / 60
    else:
        result["energy_kwh"] = 0.0

    return result


def get_daily_consumption(data: pd.DataFrame) -> pd.DataFrame:
    """Calculate total electricity consumption for each day."""
    if data is None or data.empty:
        return pd.DataFrame(columns=["date", "consumption_kwh"])

    df = data.copy()

    if "datetime" not in df.columns:
        if "Date" in df.columns:
            df["datetime"] = pd.to_datetime(df["Date"], errors="coerce")
        elif "date" in df.columns:
            df["datetime"] = pd.to_datetime(df["date"], errors="coerce")
        else:
            return pd.DataFrame(columns=["date", "consumption_kwh"])

    if not pd.api.types.is_datetime64_any_dtype(df["datetime"]):
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")

    if "energy_kwh" not in df.columns and "Global_active_power" in df.columns:
        df = calculate_energy(df)
    elif "energy_kwh" in df.columns:
        df["energy_kwh"] = pd.to_numeric(df["energy_kwh"], errors="coerce")

    df = df.dropna(subset=["datetime", "energy_kwh"])
    if df.empty:
        return pd.DataFrame(columns=["date", "consumption_kwh"])

    daily = (
        df.groupby(df["datetime"].dt.date)["energy_kwh"]
        .sum()
        .reset_index()
    )

    daily.columns = ["date", "consumption_kwh"]

    return daily


def get_hourly_consumption(data: pd.DataFrame) -> pd.DataFrame:
    """Calculate total electricity consumption for each hour."""
    if data is None or data.empty:
        return pd.DataFrame(columns=["datetime", "consumption_kwh"])

    df = data.copy()

    if "datetime" not in df.columns:
        if "Date" in df.columns:
            df["datetime"] = pd.to_datetime(df["Date"], errors="coerce")
        elif "date" in df.columns:
            df["datetime"] = pd.to_datetime(df["date"], errors="coerce")
        else:
            return pd.DataFrame(columns=["datetime", "consumption_kwh"])

    if not pd.api.types.is_datetime64_any_dtype(df["datetime"]):
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")

    if "energy_kwh" not in df.columns and "Global_active_power" in df.columns:
        df = calculate_energy(df)
    elif "energy_kwh" in df.columns:
        df["energy_kwh"] = pd.to_numeric(df["energy_kwh"], errors="coerce")

    df = df.dropna(subset=["datetime", "energy_kwh"])
    if df.empty:
        return pd.DataFrame(columns=["datetime", "consumption_kwh"])

    hourly = (
        df.groupby(df["datetime"].dt.floor("h"))["energy_kwh"]
        .sum()
        .reset_index()
    )

    hourly.columns = ["datetime", "consumption_kwh"]

    return hourly


def get_monthly_consumption(data: pd.DataFrame) -> pd.DataFrame:
    """Calculate total electricity consumption for each month."""
    if data is None or data.empty:
        return pd.DataFrame(columns=["month", "consumption_kwh"])

    df = data.copy()

    if "datetime" not in df.columns:
        if "Date" in df.columns:
            df["datetime"] = pd.to_datetime(df["Date"], errors="coerce")
        elif "date" in df.columns:
            df["datetime"] = pd.to_datetime(df["date"], errors="coerce")
        else:
            return pd.DataFrame(columns=["month", "consumption_kwh"])

    if not pd.api.types.is_datetime64_any_dtype(df["datetime"]):
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")

    if "energy_kwh" not in df.columns and "Global_active_power" in df.columns:
        df = calculate_energy(df)
    elif "energy_kwh" in df.columns:
        df["energy_kwh"] = pd.to_numeric(df["energy_kwh"], errors="coerce")

    df = df.dropna(subset=["datetime", "energy_kwh"])
    if df.empty:
        return pd.DataFrame(columns=["month", "consumption_kwh"])

    monthly = (
        df.groupby(df["datetime"].dt.to_period("M"))["energy_kwh"]
        .sum()
        .reset_index()
    )

    monthly.columns = ["month", "consumption_kwh"]
    monthly["month"] = monthly["month"].astype(str)

    return monthly


def get_average_daily_consumption(data: pd.DataFrame) -> float:
    """Calculate average daily electricity consumption."""
    if data is None or data.empty:
        return 0.0

    if "date" in data.columns and "consumption_kwh" in data.columns:
        daily = data
    else:
        daily = get_daily_consumption(data)

    if daily.empty:
        return 0.0

    valid_consumption = daily["consumption_kwh"].dropna()
    if valid_consumption.empty:
        return 0.0

    return float(valid_consumption.mean())


def get_highest_consumption_day(data: pd.DataFrame) -> InsightResult:
    """
    Identify the date with the highest daily electricity consumption.

    Args:
        data: Either a DataFrame of daily consumption (columns: 'date', 'consumption_kwh')
              or reading-level energy data (columns: 'datetime', 'energy_kwh').

    Returns:
        InsightResult (dict-like with attribute access) containing 'date' and 'consumption_kwh'.
    """
    empty_result = InsightResult({"date": None, "consumption_kwh": 0.0})

    if data is None or data.empty:
        return empty_result

    df = data.copy()
    if "date" not in df.columns and "Date" in df.columns:
        df = df.rename(columns={"Date": "date"})

    if "date" in df.columns and "consumption_kwh" in df.columns:
        daily = df
    elif "date" in df.columns and "energy_kwh" in df.columns:
        daily = df.rename(columns={"energy_kwh": "consumption_kwh"})
    elif "datetime" in df.columns:
        daily = get_daily_consumption(df)
    else:
        return empty_result

    if daily.empty:
        return empty_result

    daily = daily.dropna(subset=["date", "consumption_kwh"]).copy()
    daily["consumption_kwh"] = pd.to_numeric(daily["consumption_kwh"], errors="coerce")
    daily = daily.dropna(subset=["consumption_kwh"])

    if daily.empty:
        return empty_result

    max_idx = daily["consumption_kwh"].idxmax()
    max_row = daily.loc[max_idx]

    return InsightResult({
        "date": max_row["date"],
        "consumption_kwh": float(max_row["consumption_kwh"])
    })


def get_lowest_consumption_day(
    data: pd.DataFrame,
    daily_data: pd.DataFrame = None,
    filter_incomplete: bool = True,
    min_readings: int = 1400
) -> InsightResult:
    """
    Identify the date with the lowest daily electricity consumption,
    handling incomplete observation days appropriately.

    Args:
        data: Either a DataFrame of daily consumption (columns: 'date', 'consumption_kwh')
              or reading-level energy data (columns: 'datetime', 'energy_kwh').
        daily_data: Optional precomputed daily consumption DataFrame to avoid recalculation.
        filter_incomplete: If True and reading timestamps are present, prioritize complete days.
        min_readings: Threshold of readings per day to qualify as a complete day (default 1400 out of 1440).

    Returns:
        InsightResult with 'date', 'consumption_kwh', 'is_complete', 'reading_count', and 'filtered_incomplete_days'.
    """
    empty_result = InsightResult({
        "date": None,
        "consumption_kwh": 0.0,
        "is_complete": False,
        "reading_count": 0,
        "filtered_incomplete_days": 0
    })

    if data is None or data.empty:
        return empty_result

    df = data.copy()
    if "date" not in df.columns and "Date" in df.columns:
        df = df.rename(columns={"Date": "date"})

    if daily_data is not None and not daily_data.empty:
        daily = daily_data.copy()
    elif "date" in df.columns and "consumption_kwh" in df.columns:
        daily = df
    elif "date" in df.columns and "energy_kwh" in df.columns:
        daily = df.rename(columns={"energy_kwh": "consumption_kwh"})
    elif "datetime" in df.columns:
        daily = get_daily_consumption(df)
    else:
        return empty_result

    if "date" not in daily.columns and "Date" in daily.columns:
        daily = daily.rename(columns={"Date": "date"})

    daily = daily.dropna(subset=["date", "consumption_kwh"]).copy()
    daily["consumption_kwh"] = pd.to_numeric(daily["consumption_kwh"], errors="coerce")
    daily = daily.dropna(subset=["consumption_kwh"])

    if daily.empty:
        return empty_result

    has_reading_counts = False
    reading_counts = None
    if "datetime" in df.columns:
        if not pd.api.types.is_datetime64_any_dtype(df["datetime"]):
            df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
        valid_df = df.dropna(subset=["datetime"])
        if not valid_df.empty:
            reading_counts = valid_df.groupby(valid_df["datetime"].dt.date).size()
            has_reading_counts = True

    if filter_incomplete and has_reading_counts:
        complete_mask = reading_counts >= min_readings
        complete_dates = reading_counts[complete_mask].index
        incomplete_count = int((~complete_mask).sum())

        candidate_daily = daily[daily["date"].isin(complete_dates)]
        if not candidate_daily.empty:
            min_idx = candidate_daily["consumption_kwh"].idxmin()
            min_row = candidate_daily.loc[min_idx]
            d_val = min_row["date"]
            count_val = int(reading_counts.get(d_val, 1440))
            return InsightResult({
                "date": d_val,
                "consumption_kwh": float(min_row["consumption_kwh"]),
                "is_complete": True,
                "reading_count": count_val,
                "filtered_incomplete_days": incomplete_count
            })
        else:
            min_idx = daily["consumption_kwh"].idxmin()
            min_row = daily.loc[min_idx]
            d_val = min_row["date"]
            count_val = int(reading_counts.get(d_val, 0))
            return InsightResult({
                "date": d_val,
                "consumption_kwh": float(min_row["consumption_kwh"]),
                "is_complete": False,
                "reading_count": count_val,
                "filtered_incomplete_days": incomplete_count
            })

    min_idx = daily["consumption_kwh"].idxmin()
    min_row = daily.loc[min_idx]
    d_val = min_row["date"]
    count_val = int(reading_counts.get(d_val, 1440)) if has_reading_counts else 1440
    return InsightResult({
        "date": d_val,
        "consumption_kwh": float(min_row["consumption_kwh"]),
        "is_complete": (count_val >= min_readings) if has_reading_counts else True,
        "reading_count": count_val,
        "filtered_incomplete_days": 0
    })


def get_peak_usage_hour(data: pd.DataFrame) -> InsightResult:
    """
    Identify the hour of day with the highest average hourly electricity consumption.

    Args:
        data: Either hourly aggregated DataFrame (columns: 'datetime' or 'hour', and 'consumption_kwh')
              or reading-level energy data (columns: 'datetime', 'energy_kwh').

    Returns:
        InsightResult with 'hour' (int 0-23), 'hour_label' (e.g. '20:00 (8:00 PM)'), and 'consumption_kwh' (float).
    """
    empty_result = InsightResult({
        "hour": None,
        "hour_label": "N/A",
        "consumption_kwh": 0.0
    })

    if data is None or data.empty:
        return empty_result

    if "datetime" in data.columns and "consumption_kwh" not in data.columns:
        hourly_data = get_hourly_consumption(data)
    else:
        hourly_data = data.copy()

    if hourly_data.empty:
        return empty_result

    if "hour" not in hourly_data.columns:
        if "datetime" in hourly_data.columns:
            if not pd.api.types.is_datetime64_any_dtype(hourly_data["datetime"]):
                hourly_data["datetime"] = pd.to_datetime(hourly_data["datetime"], errors="coerce")
            hourly_data = hourly_data.dropna(subset=["datetime"])
            if hourly_data.empty:
                return empty_result
            hourly_data["hour"] = hourly_data["datetime"].dt.hour
        else:
            return empty_result

    hourly_data["consumption_kwh"] = pd.to_numeric(hourly_data["consumption_kwh"], errors="coerce")
    hourly_data = hourly_data.dropna(subset=["hour", "consumption_kwh"])

    if hourly_data.empty:
        return empty_result

    average_hourly = (
        hourly_data.groupby("hour")["consumption_kwh"]
        .mean()
        .reset_index()
    )

    if average_hourly.empty:
        return empty_result

    peak_idx = average_hourly["consumption_kwh"].idxmax()
    peak_row = average_hourly.loc[peak_idx]
    peak_hour = int(peak_row["hour"])
    peak_consumption = float(peak_row["consumption_kwh"])

    period = "AM" if peak_hour < 12 else "PM"
    display_hour = peak_hour % 12
    display_hour = 12 if display_hour == 0 else display_hour
    hour_label = f"{peak_hour:02d}:00 ({display_hour}:00 {period})"

    return InsightResult({
        "hour": peak_hour,
        "hour_label": hour_label,
        "consumption_kwh": peak_consumption
    })


def generate_consumption_summary(
    highest_day: dict,
    lowest_day: dict,
    peak_hour: dict
) -> str:
    """
    Generate an automatic, dynamic human-readable summary of electricity consumption insights.

    Args:
        highest_day: dict or InsightResult from get_highest_consumption_day
        lowest_day: dict or InsightResult from get_lowest_consumption_day
        peak_hour: dict or InsightResult from get_peak_usage_hour

    Returns:
        Formatted summary markdown string.
    """
    if (
        not highest_day or highest_day.get("date") is None or
        not lowest_day or lowest_day.get("date") is None or
        not peak_hour or peak_hour.get("hour") is None
    ):
        return "Insufficient consumption data to generate insights summary."

    h_date = str(highest_day["date"])
    h_kwh = float(highest_day["consumption_kwh"])

    l_date = str(lowest_day["date"])
    l_kwh = float(lowest_day["consumption_kwh"])
    l_note = ""
    if not lowest_day.get("is_complete", True):
        l_note = " *(based on partial day observations)*"

    raw_hour = peak_hour["hour"]
    p_label = peak_hour.get("hour_label", f"{raw_hour:02d}:00")
    p_kwh = float(peak_hour["consumption_kwh"])

    lines = [
        f"- **Highest recorded consumption** occurred on **{h_date}** with **{h_kwh:,.2f} kWh**.",
        f"- **Lowest recorded consumption** occurred on **{l_date}** with **{l_kwh:,.2f} kWh**{l_note}.",
        f"- **Electricity usage generally peaks** around **{p_label}**, averaging **{p_kwh:,.2f} kWh**."
    ]

    return "\n".join(lines)


__all__ = [
    "calculate_energy",
    "get_daily_consumption",
    "get_hourly_consumption",
    "get_monthly_consumption",
    "get_average_daily_consumption",
    "get_highest_consumption_day",
    "get_lowest_consumption_day",
    "get_peak_usage_hour",
    "generate_consumption_summary",
    "InsightResult",
]
