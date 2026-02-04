from flask import Flask, render_template, request
from main import print_task

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    title = request.form["title"]
    priority = request.form["priority"]
    print_task(title, priority)
    return "Task submitted and sent to printer!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8333)