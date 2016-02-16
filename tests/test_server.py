from pystock.server import app


def test_index():
    c = app.test_client()
    assert c.get("/").status_code == 200
