# coding: utf-8
from flask import Flask, request, jsonify
from flask import render_template as _render_template

from stock import service
from stock import config as C


app = Flask(__name__)


def render_template(name, **kw):
    kw["service"] = service
    kw["C"] = C
    return _render_template(name, **kw)


def to_int(key):
    try:
        return int(request.args.get(key))
    except:
        return None


@app.route("/", methods=["GET"])
def index():
    field_keys = [
        "ratio_closing_minus_rolling_mean_25",
        "closing_rsi_14",
        "closing_macd_minus_signal",
        "interval_closing_bollinger_band_20",
        "closing_stochastic_d_minus_sd",
    ]
    d = {k: to_int(k) for k in field_keys}
    company_list = service.company.get(**d)
    return render_template('index.html', **{"company_list": company_list})


@app.route("/company/<int:id>", methods=["GET"])
def company(id):
    company = service.company.first(id=id, raise_404=True)
    return render_template('company.html', **{"company": company})


@app.route("/api/<int:company_id>", methods=["GET"])
def api(company_id):
    company = service.company.first(id=company_id, raise_404=True)
    q = service.day_info.get(company_id)
    bbands = [{"name": "%dsigma" % s,
               "data": q.bollinger_band(sigma=s),
               "color": "black",
               "lineWidth": 0.5}
              for s in [3, 2, 1, -1, -2, -3]]
    return jsonify({
        "company": company.w.to_dict(),
        "rolling_means": [
            {"name": "rolling_mean25", "data": q.rolling_mean(period=25)},
            {"name": "rolling_mean5", "data": q.rolling_mean(period=5)},
        ] + bbands,
        "ohlc": q.ohlc(),
        "columns": [
            {"name": "volume", "data": q.volume()},
        ],
        "percentages": [
            {"name": "RSI", "data": q.RSI(period=14)},
        ],
        "macd": [
            {"name": "macd_line", "data": q.macd_line(), "yAxis": 3},
            {"name": "macd_signal", "data": q.macd_signal(), "yAxis": 3},
        ],
        "stochastic": [
            {"name": "fast %K", "data": q.stochastic_k(), "yAxis": 4},
            {"name": "fast %D / slow %K", "data": q.stochastic_d(), "yAxis": 4},
            {"name": "slow %D", "data": q.stochastic_sd(), "yAxis": 4},
        ],
    })


@app.route("/about", methods=["GET"])
def about():
    return render_template('about.html')
