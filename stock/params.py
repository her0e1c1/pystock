import inspect
from stock import line, signals

params = {
    "rolling_mean": [[25], [50], [100]],
    "bollinger_band": [[25, i] for i in range(-3, 4) if i != 0],
    "stochastic_k": [[14]],
    "stochastic_d": [[14, 3]],
    "stochastic_sd": [[14, 3, 3]],
    "rsi": [[14]],
    "macd_line": [[26, 12, 9]],  # Chris Manning (fast, slow, signal) = (17, 9, 7)
    "macd_signal": [[26, 12, 9]],
    "rolling_std": [[25]],
    "historical_volatility": [[25]],
}


def get_lines():
    funcs = {}
    for (f_name, f) in inspect.getmembers(line, inspect.isfunction):
        vals = params[f_name]
        if len(vals) == 1:
            def g(f, vs):
                def h(x):
                    return f(x, *vs)
                return h
            funcs[f_name] = g(f, vals[0])

        for vs in vals:
            name = f_name + "_" + "_".join(str(v) for v in vs)

            def g(f, vs):
                def h(x):
                    return f(x, *vs)
                return h
            funcs[name] = g(f, vs)
            # NO, cuz f and vs becomes different from next loop
            # funcs[name] = lambda x: f(x, *vs)
    return funcs


params2 = {
    "rolling_mean": [[25]],
    "rolling_mean_ratio": [[25, 25]],
    "rsi": [[14, 30, 70]],
    "stochastic": [[14, 3, 3]],
    "macd_signal": [[26, 12, 9]],
    "min_low": [[75, 1]],
    "max_high": [[100, 1]],
}


def get_signals():
    funcs = {}
    for (f_name, f) in inspect.getmembers(signals, inspect.isfunction):
        vals = params2.get(f_name, [])

        if len(vals) == 1:
            def g(f, vs):
                def h(x):
                    return f(x, *vs)
                return h
            funcs[f_name] = g(f, vals[0])

        for vs in vals:
            name = f_name + "_" + "_".join(str(v) for v in vs)

            def g(f, vs):
                def h(x):
                    return f(x, *vs)
                return h
            funcs[name] = g(f, vs)
    return funcs
