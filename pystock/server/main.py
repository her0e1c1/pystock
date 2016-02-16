import os
import datetime

from flask import Flask, render_template, request, jsonify, abort

from pystock import query


app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    company_list = []
    return render_template('index.html', **{"company_list": company_list})


@app.route("/company/", methods=["GET"])
def show_company():
    company_list = session.query(models.Company).all()
    return render_template('index.html', **{"company_list": company_list})


@app.route("/company/<int:id>", methods=["GET"])
def company(id):
    company = session.query(models.Company).filter_by(id=id).first()
    if not company:
        abort(404)
    return render_template('company.html', **{"company": company})


@app.route("/company/<int:id>/graph", methods=["GET"])
def graph(id):
    company = session.query(models.Company).filter_by(id=id).first()
    if not company:
        abort(404)

    today = datetime.date.today()
    G.Graph.month(company, today.year, today.month)

    image_dir = C.FORMAT["image_dir"].format(code=company.code)
    image_paths = []
    for f in os.listdir(image_dir):
        p = os.path.join(image_dir, f)
        p = p[p.find("/static/"):]
        image_paths.append(p)

    return render_template('graph.html', **{
        "company": company,
        "image_paths": image_paths,
    })


if __name__ == "__main__":
    from pystock import config as C
    app.run(port=C.PORT, debug=C.DEBUG)
