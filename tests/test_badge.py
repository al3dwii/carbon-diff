from carbon_diff.badge import badge


def test_badge_svg():
    resp = badge(-0.1)
    assert "svg" in resp.body.decode()
    assert "#4c1" in resp.body.decode()  # green
