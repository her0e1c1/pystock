# coding: utf-8
from flask import Flask, request, jsonify

from stock import util


app = Flask(__name__)


# @app.route("/", methods=["GET"])
# def index():
#     pass

@app.route("/api/quandl/<string:database_code>/<string:quandl_code>", methods=["GET"])
def api_get_quandl(database_code, quandl_code):
    code = "%s/%s" % (database_code, quandl_code)
    return jsonify({"series": util.df_to_series(result) + util.df_to_series(series)})


@app.route("/api/quandl/<string:database_code>/<string:quandl_code>/rolling_mean", methods=["GET"])
def rolling_api_get_quandl(database_code, quandl_code):
    code = "%s/%s" % (database_code, quandl_code)
    return jsonify({"series": util.df_to_series(df)})
