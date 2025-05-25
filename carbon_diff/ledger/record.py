import datetime as dt
import json

import typer

from ..ledger.db import get_session, init_db
from ..ledger.models import Commit

app = typer.Typer()
init_db()

@app.command()
def store(repo: str, sha: str, pr: int, delta_json: str):
    delt = json.loads(delta_json)
    with get_session() as s:
        s.add(Commit(
            sha=sha, repo=repo, pr_number=pr,
            kwh=delt["kwh"], co2=delt["co2"],
            timestamp=dt.datetime.utcnow()
        ))
        s.commit()
