"""
AWS Cost-and-Usage Report → canonical DataFrame
----------------------------------------------

* `AWSProvider.load_daily_df("YYYYMMDD")` downloads a single-day CUR CSV
  from S3, gunzips it into a temp dir, parses it with `load_cur()`,
  and returns a DataFrame with **service · region · kwh**.

The helper `load_cur()` is still publicly importable so any legacy tests
from Week 1/2 continue to work.
"""
from __future__ import annotations

import gzip
import json
import tempfile
from pathlib import Path
from typing import Final

import boto3
import pandas as pd

from .base import Provider

# --------------------------------------------------------------------------- #
# 1 · Load-time emission-factor table                                         #
# --------------------------------------------------------------------------- #

FACTOR_PATH: Final[Path] = (
    Path(__file__).with_suffix("")        # aws.py -> aws
    .parent                               # providers/
    .parent                               # carbon_diff/
    / "data"
    / "aws_factors.json"
)


def _load_factors(path: Path) -> dict[str, float]:
    """Return {region: kg-CO₂e per kWh}."""
    try:
        rows = json.load(path.open(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(
            f"Emission-factor file not found at {path}.\n"
            "Download or generate it first."
        ) from exc

    factors: dict[str, float] = {}
    for row in rows:
        mt_per_kwh = row.get("mtPerKwHour") or row.get("co2eMetricTonPerKwh")
        if mt_per_kwh is None:
            raise KeyError(
                "Row missing both 'mtPerKwHour' and 'co2eMetricTonPerKwh': "
                f"{row}"
            )
        factors[row["region"]] = float(mt_per_kwh) * 1_000  # t → kg
    return factors


_FACTORS: Final[dict[str, float]] = _load_factors(FACTOR_PATH)

# --------------------------------------------------------------------------- #
# 2 · CSV-to-DataFrame helper (unchanged from Week 1/2)                       #
# --------------------------------------------------------------------------- #


def load_cur(csv_path: str | Path) -> pd.DataFrame:
    """
    Parse an AWS CUR CSV and return exactly three columns:

        service | region | kwh

    * Treats each “RunningHour” as ≈ 1 kWh.
    * Multiplies usage by the region-specific kg-CO₂e / kWh factor.
    """
    df = pd.read_csv(
        csv_path,
        usecols=[
            "lineItem/UsageAmount",
            "product/region",
            "product/usageType",
        ],
    ).rename(
        columns={
            "lineItem/UsageAmount": "usage",
            "product/region": "region",
            "product/usageType": "service",
        },
        inplace=False,
    )

    df["kwh"] = df.apply(
        lambda r: float(r.usage) * _FACTORS.get(r.region, 0.0),
        axis=1,
    )
    return df[["service", "region", "kwh"]]


# --------------------------------------------------------------------------- #
# 3 · Provider subclass used by Week-3 config loader                           #
# --------------------------------------------------------------------------- #


class AWSProvider(Provider):
    """
    Concrete Provider for AWS Cost-and-Usage Reports stored in S3.

    Parameters
    ----------
    bucket : str
        Name of the S3 bucket that holds `YYYYMMDD-Usage.csv.gz` objects.
    prefix : str, default ""
        Optional key prefix inside the bucket.
    """

    def __init__(self, bucket: str, prefix: str = "") -> None:
        self.bucket = bucket
        self.prefix = prefix
        self._s3 = boto3.client("s3")

    # --------------------------------------------------------------------- #
    # Provider API                                                          #
    # --------------------------------------------------------------------- #

    def load_daily_df(self, date: str) -> pd.DataFrame:  # YYYYMMDD
        """Download, gunzip, parse, and return the kWh DataFrame."""
        key = f"{self.prefix}{date}-Usage.csv.gz"

        with tempfile.TemporaryDirectory() as tmp:
            gz_path = Path(tmp) / "cur.csv.gz"
            self._s3.download_file(self.bucket, key, str(gz_path))

            csv_path = gz_path.with_suffix("")  # strip ".gz"
            with gzip.open(gz_path, "rb") as f_in, csv_path.open("wb") as f_out:
                f_out.write(f_in.read())

            return load_cur(csv_path)


__all__ = ["AWSProvider", "load_cur"]
