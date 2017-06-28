import inspect
from stock import charts

params = {
    "rolling_mean": [[25], [50], [100]],
    "bollinger_band": [[25, i] for i in range(-3, 4) if i != 0],
    "stochastic_k": [[14]],
    "stochastic_d": [[14, 3]],
    "stochastic_sd": [[14, 3, 3]],
    "rsi": [[14]],
    "macd_line": [[26, 12, 9]],  # Chris Manning (fast, slow, signal) = (17, 9, 7)
    "macd_signal": [[26, 12, 9]],
}


def get_charts():
    funcs = {}
    for (f_name, f) in inspect.getmembers(charts, inspect.isfunction):
        vals = params[f_name]
        if len(vals) == 1:
            funcs[f_name] = lambda x: f(x, *vs)
        for vs in vals:
            name = f_name + "_" + "_".join(str(v) for v in vs)
            funcs[name] = lambda x: f(x, *vs)
    return funcs
