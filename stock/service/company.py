def _percent(q, kw, col_name):
    if col_name not in kw or kw[col_name] is None:
        return q
    val = kw[col_name]
    col = getattr(query.models.CompanySearchField, col_name)
    if val >= 0:
        q = q.filter(col >= val)
    else:
        q = q.filter(col < val)
    return q


def _cross(q, kw, val_name, format_col_name):
    if val_name not in kw or kw[val_name] is None:
        return q

    col_name1 = format_col_name % 1
    col_name2 = format_col_name % 2
    v = kw[val_name]
    col1 = getattr(query.models.CompanySearchField, col_name1)
    col2 = getattr(query.models.CompanySearchField, col_name2)
    if v > 0:
        # Golden cross
        q = q.filter(col1 >= 0)
        q = q.filter(col2 <= 0)
    else:
        # Dead cross
        q = q.filter(col1 <= 0)
        q = q.filter(col2 >= 0)
    return q


def get(**kw):
    session = query.models.Session()
    q = query.Company.query(session)
    if any(kw.values()):
        q = q.join(query.models.Company.search_field)

    q = _percent(q, kw, "ratio_closing_minus_rolling_mean_25")
    q = _percent(q, kw, "ratio_closing1_minus_closing2")

    q = _cross(q, kw, "closing_stochastic_d_minus_sd", "closing_stochastic_d_minus_sd%d_14_3_3")
    q = _cross(q, kw, "closing_macd_minus_signal", "closing_macd_minus_signal%d_26_12_9")

    if kw["closing_rsi_14"] is not None:
        rsi = kw["closing_rsi_14"]
        col = query.models.CompanySearchField.closing_rsi_14
        if rsi >= 0:
            q = q.filter(col >= rsi)
        else:
            rsi *= -1
            q = q.filter(col < rsi)

    if kw["interval_closing_bollinger_band_20"] is not None:
        col_name = "interval_closing_bollinger_band_20"
        v = kw["interval_closing_bollinger_band_20"]
        col = getattr(query.models.CompanySearchField, col_name)
        q = q.filter(col == v)

    return q.all()
