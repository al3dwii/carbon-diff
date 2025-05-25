from carbon_diff.providers.azure import AzureProvider


def test_azure_fixture():
    p = AzureProvider("fixtures/azure")
    df = p.load_daily_df("20240524")
    assert {"service", "region", "kwh"} <= set(df.columns)
    assert not df.kwh.isna().any()
