from datetime import datetime

from sqlmodel import Field, SQLModel


class Commit(SQLModel, table=True):
    sha: str = Field(primary_key=True)
    repo: str
    pr_number: int
    kwh: float
    co2: float
    timestamp: datetime
