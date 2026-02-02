from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd


REQUIRED_COLUMNS = [
    "date", "provider", "account", "service", "cost", "currency", "tag_env", "tag_team"
]


@dataclass
class BillingData:
    df: pd.DataFrame


class BillingLoader:
    """
    Loads and normalizes billing data from a CSV.
    This keeps the demo simple (no cloud creds) while still proving FinOps skill.
    """

    def __init__(self, csv_path: str):
        self.csv_path = Path(csv_path)
        self._cache: Optional[BillingData] = None

    def load(self, force_reload: bool = False) -> BillingData:
        if self._cache is not None and not force_reload:
            return self._cache

        if not self.csv_path.exists():
            raise FileNotFoundError(f"Billing CSV not found: {self.csv_path}")

        df = pd.read_csv(self.csv_path)

        # Validate columns (simple and explicit for recruiter readability)
        missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
        if missing:
            raise ValueError(f"CSV missing required columns: {missing}")

        # Normalize types
        df["date"] = pd.to_datetime(df["date"], errors="raise").dt.date
        df["cost"] = pd.to_numeric(df["cost"], errors="raise").astype(float)

        # Normalize tags: treat empty strings / NaN as None
        for col in ["tag_env", "tag_team"]:
            df[col] = df[col].astype("string").replace({"": None, "nan": None})

        self._cache = BillingData(df=df)
        return self._cache