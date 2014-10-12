from flask import Flask, render_template, request, jsonify
import config as C
import models

app = Flask(__name__)
app.session = models.initial_session()

@app.route("/", methods=["GET"])
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.debug = C.DEBUG
    app.run(host="0.0.0.0")
