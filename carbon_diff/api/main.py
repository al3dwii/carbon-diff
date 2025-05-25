import datetime as dt
from typing import List

from fastapi import FastAPI
from sqlmodel import select

from ..ledger.db import get_session
from ..ledger.models import Commit

app = FastAPI(title="Carbon Diff API")

@app.get("/deltas/{repo}", response_model=List[Commit])
def repo_deltas(repo: str, days: int = 30):
    cutoff = dt.datetime.utcnow() - dt.timedelta(days=days)
    with get_session() as s:
        return s.exec(
            select(Commit).where(
                Commit.repo == repo,
                Commit.timestamp >= cutoff
            ).order_by(Commit.timestamp)
        ).all()
