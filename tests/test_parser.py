from carbon_diff.providers.aws import load_cur


def test_load_cur_shape():
    df = load_cur("fixtures/aws/sample.csv")
    assert set(df.columns) == {"service", "region", "kwh"}
    assert df.kwh.sum() > 0
