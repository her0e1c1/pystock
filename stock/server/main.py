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
        "ratio_closing1_minus_closing2",
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
    return jsonify({
        "company": company.w.to_dict(),
        "series": q.to_series(),
    })


@app.route("/about", methods=["GET"])
def about():
    return render_template('about.html')
