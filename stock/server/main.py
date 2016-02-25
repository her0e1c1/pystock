# coding: utf-8
from flask import Flask, render_template, request, jsonify, abort

from stock import query
from stock import service
from stock import config as C


app = Flask(__name__)


def to_int(key):
    try:
        return int(request.args.get(key))
    except:
        return None


@app.route("/", methods=["GET"])
def index():
    try:
        v = int(request.args.get("ratio_closing_minus_rolling_mean_25"))
    except:
        v = None
    try:
        v2 = int(request.args.get("closing_rsi_14"))
    except:
        v2 = None
    try:
        v3 = int(request.args.get("closing_macd_minus_signal"))
    except:
        v3 = None
    try:
        v4 = int(request.args.get("interval_closing_bollinger_band_20"))
    except:
        v4 = None

    company_list = service.get_companies(
        ratio_closing_minus_rolling_mean_25=v,
        closing_rsi_14=v2,
        closing_macd_minus_signal=v3,
        interval_closing_bollinger_band_20=v4,
        closing_stochastic_d_minus_sd=to_int("closing_stochastic_d_minus_sd"),
    )
    return render_template('index.html', **{"company_list": company_list,
                                            "last_date": service.last_date()})


@app.route("/company/<int:id>", methods=["GET"])
def company(id):
    company = query.Company.first(id=id)
    if not company:
        abort(404)
    return render_template('company.html', **{"company": company})


@app.route("/api/<int:company_id>", methods=["GET"])
def api(company_id):
    company = query.Company.first(id=company_id)
    if not company:
        abort(404)
    q = query.DayInfo.get(company_id)
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


@app.route("/links", methods=["GET"])
def links():
    return render_template('links.html', **{"C": C})
