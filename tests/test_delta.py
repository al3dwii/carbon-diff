import pandas as pd

from carbon_diff.diff import energy_delta


def test_delta_zero():
    df = pd.DataFrame({"kwh": [1, 2, 3]})
    assert energy_delta(df, df)["kwh"] == 0
