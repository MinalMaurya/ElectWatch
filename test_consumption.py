
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


DATA_PATH = "data/household_power_consumption.txt"


# Load and clean dataset
raw_data = load_electricity_data(DATA_PATH)
cleaned_data = clean_electricity_data(raw_data)

# Calculate energy
energy_data = calculate_energy(cleaned_data)


print("\nELECTWATCH - CONSUMPTION ANALYSIS")

print("\nFirst five energy readings:")
print(energy_data[["datetime", "Global_active_power", "energy_kwh"]].head())


# Daily consumption
daily = get_daily_consumption(energy_data)

print("\nFirst five daily consumption records:")
print(daily.head())


# Hourly consumption
hourly = get_hourly_consumption(energy_data)

print("\nFirst five hourly consumption records:")
print(hourly.head())


# Monthly consumption
monthly = get_monthly_consumption(energy_data)

print("\nFirst five monthly consumption records:")
print(monthly.head())


# Average daily consumption
average = get_average_daily_consumption(energy_data)

print("\nAverage daily consumption:")
print(f"{average:.4f} kWh")


# Total consumption
total = energy_data["energy_kwh"].sum()

print("\nTotal electricity consumption:")
print(f"{total:.2f} kWh")


# Consumption Insights
highest = get_highest_consumption_day(daily)
lowest = get_lowest_consumption_day(energy_data, daily_data=daily)
peak = get_peak_usage_hour(hourly)
summary = generate_consumption_summary(highest, lowest, peak)

print("\n--- CONSUMPTION INSIGHTS ---")
print(f"Highest Consumption Day: {highest['date']} ({highest['consumption_kwh']:.2f} kWh)")
print(f"Lowest Consumption Day: {lowest['date']} ({lowest['consumption_kwh']:.2f} kWh, Complete: {lowest['is_complete']})")
print(f"Peak Usage Hour: {peak['hour_label']} ({peak['consumption_kwh']:.2f} kWh avg)")
print("\nAutomatic Summary:")
print(summary)

