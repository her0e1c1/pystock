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


@app.route("/api/<int:company_id>", methods=["GET"])
def api(company_id):
    print(request)
    company = query.Company.first(id=company_id)
    if not company:
        abort(404)
    return jsonify({
        "company": company.w.to_dict(),
        "day_info_list": query.DayInfo.get(company_id).to_series()
    })
