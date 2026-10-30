
from src.data_loader import load_electricity_data
from src.data_cleaner import clean_electricity_data

from src.consumption import (
    calculate_energy,
    get_daily_consumption,
    get_hourly_consumption,
    get_monthly_consumption
)

from src.visualizations import (
    plot_daily_consumption,
    plot_monthly_consumption,
    plot_hourly_consumption
)


DATA_PATH = "data/household_power_consumption.txt"

# Load and prepare data
raw_data = load_electricity_data(DATA_PATH)
cleaned_data = clean_electricity_data(raw_data)
energy_data = calculate_energy(cleaned_data)

# Generate aggregated data
daily = get_daily_consumption(energy_data)
hourly = get_hourly_consumption(energy_data)
monthly = get_monthly_consumption(energy_data)

# Generate charts
daily_chart = plot_daily_consumption(daily)
monthly_chart = plot_monthly_consumption(monthly)
hourly_chart = plot_hourly_consumption(hourly)

# Save charts as HTML files
daily_chart.write_html("daily_consumption.html")
monthly_chart.write_html("monthly_consumption.html")
hourly_chart.write_html("hourly_consumption.html")

print("\nVISUALIZATION TEST COMPLETED")
print("Generated:")
print("1. daily_consumption.html")
print("2. monthly_consumption.html")
print("3. hourly_consumption.html")