import os
import datetime

from flask import Flask, render_template, request, jsonify, abort

from pystock import query


app = Flask(__name__)


@app.route("/", methods=["GET"])
@app.route("/company/", methods=["GET"])
def index():
    return render_template('index.html', **{"company_list": query.Company.query()})


@app.route("/company/<int:id>", methods=["GET"])
def company(id):
    company = query.Company.first(id=id)
    if not company:
        abort(404)
    return render_template('company.html', **{"company": company})


if __name__ == "__main__":
    from pystock import config as C
    app.run(port=C.PORT, debug=C.DEBUG)
