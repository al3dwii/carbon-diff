from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class Provider(ABC):
    """
    Every cloud-provider implementation must return a DataFrame with
    columns: service, region, kwh   — one row per line-item for a *single* day.
    """

    @abstractmethod
    def load_daily_df(self, date: str) -> pd.DataFrame:
        """Load usage for one UTC calendar day (format YYYYMMDD)."""
