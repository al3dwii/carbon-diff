from carbon_diff.config import load_providers


def test_load():
    providers = load_providers("fixtures/cdiff_multi.yml")
    assert len(providers) == 3
