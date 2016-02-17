from pystock.server import app
from pystock import query


def test_index():
    c = app.test_client()
    assert c.get("/").status_code == 200


def test_company():
    c = app.test_client()
    company = query.Company.first()
    assert c.get("/company/%s" % company.id).status_code == 200
