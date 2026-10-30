
import pandas as pd
from pathlib import Path


def load_electricity_data(file_path: str) -> pd.DataFrame:
    """
    Load household electricity consumption data.

    Args:
        file_path: Path to the electricity dataset.

    Returns:
        A pandas DataFrame containing electricity readings.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    if path.stat().st_size == 0:
        raise ValueError("Dataset file is empty.")

    data = pd.read_csv(
        path,
        sep=";",
        na_values=["?"],
        low_memory=False
    )

    return data

