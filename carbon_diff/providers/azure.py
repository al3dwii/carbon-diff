"""Azure CSV → canonical DataFrame."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .base import Provider

# ----- load kg-CO₂e / kWh factors --------------------------------------
FACTOR_PATH = Path(__file__).parent.parent / "data" / "azure_factors.json"
_FACTORS = {row["region"]: float(row["kgCO2ePerKwh"])
            for row in json.load(open(FACTOR_PATH, encoding="utf-8"))}

class AzureProvider(Provider):
    def __init__(self, csv_dir: str | Path):
        self.csv_dir = Path(csv_dir)

    def load_daily_df(self, date: str) -> pd.DataFrame:          # YYYYMMDD
        csv = self.csv_dir / f"{date}.csv"
        df = pd.read_csv(
            csv,
            usecols=["meterName", "resourceLocation", "usageQuantity"],
        ).rename(
            columns={
                "meterName": "service",
                "resourceLocation": "region",
                "usageQuantity": "usage",
            },
            inplace=False,
        )
        df["kwh"] = df.apply(
            lambda r: float(r.usage) * _FACTORS.get(r.region, 0.0),
            axis=1,
        )
        return df[["service", "region", "kwh"]]
