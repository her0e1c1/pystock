# coding: utf-8

# return pd.DataFrame.from_records([{}])


def golden_cross(ins, format_string):
    v1 = getattr(ins, format_string % 1)
    v2 = getattr(ins, format_string % 2)
    return v1 > 0 and v2 < 0


def dead_cross(ins, format_string):
    v1 = getattr(ins, format_string % 1)
    v2 = getattr(ins, format_string % 2)
    return v1 < 0 and v2 > 0


buy_conditions = {
    "closing_rsi_14": lambda ins: ins.closing_rsi_14 <= 30,
    "closing_macd_minus_signal": lambda ins: golden_cross(ins, "closing_macd_minus_signal%s_26_12_9"),
    "ratio_closing_minus_rolling_mean_25": lambda ins: ins.ratio_closing_minus_rolling_mean_25 <= -10,
    "interval_closing_bollinger_band_20": lambda ins: ins.interval_closing_bollinger_band_20 <= -3,
}

sell_conditions = {
    "closing_rsi_14": lambda ins: ins.closing_rsi_14 >= 70,
    "closing_macd_minus_signal": lambda ins: dead_cross(ins, "closing_macd_minus_signal%s_26_12_9"),
    "ratio_closing_minus_rolling_mean_25": lambda ins: ins.ratio_closing_minus_rolling_mean_25 >= 10,
    "interval_closing_bollinger_band_20": lambda ins: ins.interval_closing_bollinger_band_20 >= 3,
}
