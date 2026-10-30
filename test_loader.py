
from src.data_loader import load_electricity_data

DATA_PATH = "data/household_power_consumption.txt"

data = load_electricity_data(DATA_PATH)

print("\nDataset loaded successfully!")

print("\nFirst five rows:")
print(data.head())

print("\nDataset shape:")
print(data.shape)

print("\nColumn names:")
print(data.columns.tolist())

print("\nMissing values:")
print(data.isnull().sum())

