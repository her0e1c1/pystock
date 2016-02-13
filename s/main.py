import os
import datetime
from flask import Flask, render_template, request, jsonify, abort
import s.config as C

from s import models
from s import graph as G

app = Flask(__name__)
session = models.Session()


@app.route("/", methods=["GET"])
def index():
    # company_list = session.query(models.Company).all()
    company_list = []
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
    app.debug = C.DEBUG
    app.run(host="0.0.0.0")
