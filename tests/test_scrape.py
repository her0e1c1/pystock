import pytest


@pytest.mark.parametrize("code", [1909])
def test_yahoo_japan(code):
    from pystock.scrape import YahooJapan
    yahoo = YahooJapan()
    assert yahoo.current_value(code) > 0
    assert len(yahoo.split_stock_date(code, page=1)) >= 0
    assert len(yahoo.history(code, page=1)) > 0
