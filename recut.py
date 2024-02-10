
from flask import Flask, send_from_directory

import os

arr = os.listdir("static")
print(arr);


app = Flask(__name__, static_url_path="")

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)



# @app.route('/<path:path>')
# def send_report(path):
#     println("path " + path);
#     return send_from_directory('static', path)