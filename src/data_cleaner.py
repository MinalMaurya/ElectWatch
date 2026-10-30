
import pandas as pd


NUMERIC_COLUMNS = [
    "Global_active_power",
    "Global_reactive_power",
    "Voltage",
    "Global_intensity",
    "Sub_metering_1",
    "Sub_metering_2",
    "Sub_metering_3"
]


def clean_electricity_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Clean household electricity consumption data.

    Returns:
        Cleaned DataFrame with valid timestamps
        and active power readings.
    """

    cleaned_data = data.copy()

    # Combine Date and Time into one datetime column
    cleaned_data["datetime"] = pd.to_datetime(
        cleaned_data["Date"] + " " + cleaned_data["Time"],
        format="%d/%m/%Y %H:%M:%S",
        errors="coerce"
    )

    # Convert measurement columns into numeric values
    for column in NUMERIC_COLUMNS:
        cleaned_data[column] = pd.to_numeric(
            cleaned_data[column],
            errors="coerce"
        )

    # Remove records with invalid timestamps
    cleaned_data = cleaned_data.dropna(
        subset=["datetime"]
    )

    # Remove records without the main electricity measurement
    cleaned_data = cleaned_data.dropna(
        subset=["Global_active_power"]
    )

    # Sort readings chronologically
    cleaned_data = cleaned_data.sort_values(
        by="datetime"
    )

    # Reset row indexes
    cleaned_data = cleaned_data.reset_index(drop=True)

    return cleaned_data
