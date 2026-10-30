
from src.data_loader import load_electricity_data
from src.data_cleaner import clean_electricity_data

DATA_PATH = "data/household_power_consumption.txt"

# Load original data
raw_data = load_electricity_data(DATA_PATH)

# Clean the data
cleaned_data = clean_electricity_data(raw_data)

print("\nDATA CLEANING COMPLETED")

print("\nOriginal dataset shape:")
print(raw_data.shape)

print("\nCleaned dataset shape:")
print(cleaned_data.shape)

print("\nFirst five cleaned records:")
print(cleaned_data.head())

print("\nRemaining missing values:")
print(cleaned_data.isnull().sum())

print("\nDatetime column type:")
print(cleaned_data["datetime"].dtype)

print("\nDate range:")
print(cleaned_data["datetime"].min())
print(cleaned_data["datetime"].max())
