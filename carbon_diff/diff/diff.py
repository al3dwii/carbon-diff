from __future__ import annotations

from typing import TypedDict

import pandas as pd


class Delta(TypedDict):
    kwh: float
    co2: float


def energy_delta(baseline: pd.DataFrame, pr: pd.DataFrame) -> Delta:
    """Difference = PR – baseline (positive = worse)."""
    kwh_diff = pr.kwh.sum() - baseline.kwh.sum()
    return {
        "kwh": round(kwh_diff, 3),
        # 0.4 kg CO₂ per kWh (global avg) — refine later
        "co2": round(kwh_diff * 0.4, 3),
    }
