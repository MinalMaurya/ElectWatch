
import unittest
import datetime
import pandas as pd
import numpy as np

from src.consumption import (
    calculate_energy,
    get_daily_consumption,
    get_hourly_consumption,
    get_monthly_consumption,
    get_average_daily_consumption,
    get_highest_consumption_day,
    get_lowest_consumption_day,
    get_peak_usage_hour,
    generate_consumption_summary,
    InsightResult
)


class TestConsumptionInsights(unittest.TestCase):

    def setUp(self):
        # Create a controlled synthetic dataset:
        # Day 1: 2023-01-01, 1440 readings (complete), 0.02 kWh each -> total 28.8 kWh
        # Day 2: 2023-01-02, 1440 readings (complete), 0.05 kWh each -> total 72.0 kWh
        # Day 3: 2023-01-03, 30 readings (incomplete), 0.01 kWh each -> total 0.3 kWh
        dt1 = pd.date_range("2023-01-01 00:00", periods=1440, freq="min")
        dt2 = pd.date_range("2023-01-02 00:00", periods=1440, freq="min")
        dt3 = pd.date_range("2023-01-03 00:00", periods=30, freq="min")

        self.synthetic_energy = pd.DataFrame({
            "datetime": dt1.append(dt2).append(dt3),
            "energy_kwh": [0.02] * 1440 + [0.05] * 1440 + [0.01] * 30
        })

        self.synthetic_daily = get_daily_consumption(self.synthetic_energy)
        self.synthetic_hourly = get_hourly_consumption(self.synthetic_energy)

    def test_imports_from_consumption(self):
        self.assertTrue(callable(get_highest_consumption_day))
        self.assertTrue(callable(get_lowest_consumption_day))
        self.assertTrue(callable(get_peak_usage_hour))
        self.assertTrue(callable(generate_consumption_summary))

    def test_highest_consumption_day(self):
        result = get_highest_consumption_day(self.synthetic_daily)
        self.assertEqual(result["date"], datetime.date(2023, 1, 2))
        self.assertAlmostEqual(result["consumption_kwh"], 72.0, places=2)
        # Test attribute access
        self.assertEqual(result.date, datetime.date(2023, 1, 2))
        self.assertAlmostEqual(result.consumption_kwh, 72.0, places=2)

    def test_highest_consumption_day_from_energy_data(self):
        result = get_highest_consumption_day(self.synthetic_energy)
        self.assertEqual(result["date"], datetime.date(2023, 1, 2))
        self.assertAlmostEqual(result["consumption_kwh"], 72.0, places=2)

    def test_highest_consumption_day_empty(self):
        result = get_highest_consumption_day(pd.DataFrame())
        self.assertIsNone(result["date"])
        self.assertEqual(result["consumption_kwh"], 0.0)

    def test_highest_consumption_day_missing_values(self):
        # DataFrame with NaN values
        df = pd.DataFrame({
            "date": [datetime.date(2023, 1, 1), datetime.date(2023, 1, 2), datetime.date(2023, 1, 3)],
            "consumption_kwh": [np.nan, 45.0, np.nan]
        })
        result = get_highest_consumption_day(df)
        self.assertEqual(result["date"], datetime.date(2023, 1, 2))
        self.assertAlmostEqual(result["consumption_kwh"], 45.0, places=2)

        # All-NaN DataFrame
        df_all_nan = pd.DataFrame({
            "date": [datetime.date(2023, 1, 1), datetime.date(2023, 1, 2)],
            "consumption_kwh": [np.nan, np.nan]
        })
        result_nan = get_highest_consumption_day(df_all_nan)
        self.assertIsNone(result_nan["date"])
        self.assertEqual(result_nan["consumption_kwh"], 0.0)

    def test_highest_consumption_day_string_datetime_conversion(self):
        # Data with string datetime
        df = pd.DataFrame({
            "datetime": ["2023-01-01 10:00:00", "2023-01-01 10:01:00", "2023-01-02 12:00:00"],
            "energy_kwh": [1.0, 2.0, 5.0]
        })
        result = get_highest_consumption_day(df)
        self.assertEqual(result["date"], datetime.date(2023, 1, 2))
        self.assertAlmostEqual(result["consumption_kwh"], 5.0, places=2)

    def test_lowest_consumption_day_filters_incomplete(self):
        # Even though 2023-01-03 has 0.3 kWh, it is incomplete (30 readings < 1400)
        # Therefore, the lowest complete day should be 2023-01-01 (28.8 kWh)
        result = get_lowest_consumption_day(self.synthetic_energy, daily_data=self.synthetic_daily)
        self.assertEqual(result["date"], datetime.date(2023, 1, 1))
        self.assertAlmostEqual(result["consumption_kwh"], 28.8, places=2)
        self.assertTrue(result["is_complete"])
        self.assertEqual(result["filtered_incomplete_days"], 1)

    def test_lowest_consumption_day_raw_without_filtering(self):
        # When filter_incomplete is False, it returns the minimum raw day (2023-01-03, 0.3 kWh)
        result = get_lowest_consumption_day(
            self.synthetic_energy,
            daily_data=self.synthetic_daily,
            filter_incomplete=False
        )
        self.assertEqual(result["date"], datetime.date(2023, 1, 3))
        self.assertAlmostEqual(result["consumption_kwh"], 0.3, places=2)
        self.assertFalse(result["is_complete"])

    def test_lowest_consumption_day_fallback_when_only_incomplete_days(self):
        # Range with only the incomplete day
        only_incomplete = self.synthetic_energy[
            self.synthetic_energy["datetime"].dt.date == datetime.date(2023, 1, 3)
        ]
        result = get_lowest_consumption_day(only_incomplete)
        self.assertEqual(result["date"], datetime.date(2023, 1, 3))
        self.assertAlmostEqual(result["consumption_kwh"], 0.3, places=2)
        self.assertFalse(result["is_complete"])

    def test_lowest_consumption_day_empty(self):
        result = get_lowest_consumption_day(pd.DataFrame())
        self.assertIsNone(result["date"])
        self.assertEqual(result["consumption_kwh"], 0.0)
        self.assertFalse(result["is_complete"])

    def test_peak_usage_hour(self):
        times = pd.date_range("2023-01-01 00:00", periods=24, freq="h")
        kwh_values = [1.0] * 24
        kwh_values[19] = 5.5  # Hour 19 has highest consumption

        hourly_df = pd.DataFrame({
            "datetime": times,
            "consumption_kwh": kwh_values
        })

        result = get_peak_usage_hour(hourly_df)
        self.assertEqual(result["hour"], 19)
        self.assertIn("19:00", result["hour_label"])
        self.assertIn("7:00 PM", result["hour_label"])
        self.assertAlmostEqual(result["consumption_kwh"], 5.5, places=2)

    def test_peak_usage_hour_empty(self):
        result = get_peak_usage_hour(pd.DataFrame())
        self.assertIsNone(result["hour"])
        self.assertEqual(result["hour_label"], "N/A")
        self.assertEqual(result["consumption_kwh"], 0.0)

    def test_generate_consumption_summary_complete(self):
        h = {"date": "2023-01-02", "consumption_kwh": 72.0}
        l = {"date": "2023-01-01", "consumption_kwh": 28.8, "is_complete": True}
        p = {"hour": 19, "hour_label": "19:00 (7:00 PM)", "consumption_kwh": 5.5}

        summary = generate_consumption_summary(h, l, p)
        self.assertIn("2023-01-02", summary)
        self.assertIn("72.00 kWh", summary)
        self.assertIn("2023-01-01", summary)
        self.assertIn("28.80 kWh", summary)
        self.assertIn("19:00 (7:00 PM)", summary)
        self.assertIn("5.50 kWh", summary)
        self.assertNotIn("partial day", summary)

    def test_generate_consumption_summary_partial(self):
        h = {"date": "2023-01-03", "consumption_kwh": 0.3}
        l = {"date": "2023-01-03", "consumption_kwh": 0.3, "is_complete": False}
        p = {"hour": 0, "hour_label": "00:00 (12:00 AM)", "consumption_kwh": 0.3}

        summary = generate_consumption_summary(h, l, p)
        self.assertIn("partial day", summary)

    def test_generate_consumption_summary_empty(self):
        summary = generate_consumption_summary({}, {}, {})
        self.assertIn("Insufficient", summary)

    def test_date_range_filtering_simulation(self):
        filtered = self.synthetic_energy[
            self.synthetic_energy["datetime"].dt.date == datetime.date(2023, 1, 1)
        ]
        daily_filt = get_daily_consumption(filtered)
        hourly_filt = get_hourly_consumption(filtered)

        high = get_highest_consumption_day(daily_filt)
        low = get_lowest_consumption_day(filtered, daily_data=daily_filt)
        peak = get_peak_usage_hour(hourly_filt)

        self.assertEqual(high["date"], datetime.date(2023, 1, 1))
        self.assertEqual(low["date"], datetime.date(2023, 1, 1))
        self.assertAlmostEqual(high["consumption_kwh"], 28.8, places=2)
        self.assertAlmostEqual(low["consumption_kwh"], 28.8, places=2)
        self.assertTrue(low["is_complete"])


if __name__ == "__main__":
    unittest.main()
