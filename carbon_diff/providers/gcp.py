import json
from pathlib import Path

import pandas as pd
from google.cloud import bigquery

from .base import Provider

_FACTORS = {
    row["region"]: float(row["mtPerKwHour"]) * 1000
    for row in json.load(open(Path(__file__).parent.parent / "data" / "gcp_factors.json"))
}

class GCPProvider(Provider):
    def __init__(self, project: str):
        self.client = bigquery.Client(project=project)
        self.dataset = "billing_export"

    def load_daily_df(self, date: str) -> pd.DataFrame:
        sql = f"""
        SELECT service.description AS service,
               location.location AS region,
               usage.amount AS usage
        FROM `{self.client.project}.{self.dataset}.gcp_billing_export_v1_*`
        WHERE _PARTITIONTIME = "{date}"
        """
        df = self.client.query(sql).result().to_dataframe()
        df["kwh"] = df.apply(
            lambda r: float(r.usage) * _FACTORS.get(r.region, 0), axis=1
        )
        return df[["service", "region", "kwh"]]
