# carbon_diff/cli.py
from __future__ import annotations

import json
import os
import subprocess
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional  # ← added Optional

import boto3
import pandas as pd
import typer
from rich.console import Console
from rich.table import Table

from .config import load_providers
from .diff import energy_delta
from .providers.aws import load_cur

app = typer.Typer(help="Carbon Diff CLI")
console = Console()

# ──────────────────────────────────────────────────────────────────────────────
# 1 ▸ legacy helper – compare two local AWS CUR CSVs
# ──────────────────────────────────────────────────────────────────────────────
@app.command()
def diff(baseline: str, pr: str):
    """Compare two AWS CUR CSV files already on disk."""
    base_df = load_cur(baseline)
    pr_df = load_cur(pr)
    _render_delta(base_df, pr_df)


# ──────────────────────────────────────────────────────────────────────────────
# 2 ▸ Week-3 command – multi-provider for a single UTC day
# ──────────────────────────────────────────────────────────────────────────────
@app.command()
def diff_day(date_: str = typer.Option(..., help="YYYYMMDD")):
    """Aggregate every provider in *cdiff.yml* and compare day-to-day."""
    providers = load_providers()

    pr_df = pd.concat(
        [p.load_daily_df(date_) for p in providers], ignore_index=True
    )

    day_minus_one = (
        datetime.strptime(date_, "%Y%m%d") - timedelta(days=1)
    ).strftime("%Y%m%d")

    base_df = pd.concat(
        [p.load_daily_df(day_minus_one) for p in providers], ignore_index=True
    )

    _render_delta(base_df, pr_df)


# ──────────────────────────────────────────────────────────────────────────────
# 3 ▸ GitHub-Action entry-point
#     • real mode  → needs aws_bucket   → downloads CUR CSVs
#     • dummy mode → aws_bucket omitted → emits zero delta
# ──────────────────────────────────────────────────────────────────────────────
@app.command()
def action(
    aws_bucket: Optional[str] = typer.Option(  # ← Optional fixes Typer crash
        None,
        help=(
            "S3 bucket holding CUR CSVs (omit to run in dummy mode "
            "without AWS)"
        ),
    ),
    baseline_days: int = typer.Option(
        1, help="Days back from today for baseline CSV"
    ),
):
    """Docker-Action entry-point used in CI/CD pipelines."""
    # ── dummy fast-path ────────────────────────────────────────────────────
    if aws_bucket is None:
        delta = {"kwh": 0.0, "co2": 0.0}
        _emit_delta(delta)
        return

    # ── real AWS CUR path ────────────────────────────────────────────────
    s3 = boto3.client("s3")
    today = date.today()
    cur_key = f"{today:%Y%m%d}-Usage.csv.gz"
    base_key = f"{today - timedelta(days=baseline_days):%Y%m%d}-Usage.csv.gz"

    with tempfile.TemporaryDirectory() as tmp:
        cur_path = Path(tmp) / "cur.csv.gz"
        base_path = Path(tmp) / "base.csv.gz"

        s3.download_file(aws_bucket, cur_key, str(cur_path))
        s3.download_file(aws_bucket, base_key, str(base_path))
        subprocess.run(["gunzip", str(cur_path), str(base_path)], check=True)

        cur_df = load_cur(cur_path.with_suffix(""))
        base_df = load_cur(base_path.with_suffix(""))
        delta = energy_delta(base_df, cur_df)

    _emit_delta(delta)


# ──────────────────────────────────────────────────────────────────────────────
# 4 ▸ helpers
# ──────────────────────────────────────────────────────────────────────────────
def _emit_delta(delta: dict) -> None:
    """Write delta both to stdout and to the DELTA_JSON env-var for later steps."""
    payload = json.dumps(delta, separators=(",", ":"))
    os.environ["DELTA_JSON"] = payload
    print(payload)


    # If we're running *inside* a GitHub Actions step, expose the same
    # payload as a proper step output so the next steps can read it.
    if "GITHUB_OUTPUT" in os.environ:
       with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
            fh.write(f"delta_json={payload}\n")


def _render_delta(base_df: pd.DataFrame, pr_df: pd.DataFrame) -> None:
    delta = energy_delta(base_df, pr_df)
    sign = "🟥+" if delta["kwh"] > 0 else "🟩"
    table = Table(title="Carbon Diff")
    table.add_column("Δ kWh")
    table.add_column("Δ CO₂ (kg)")
    table.add_row(f"{sign}{delta['kwh']:.2f}", f"{sign}{delta['co2']:.2f}")
    console.print(table)
