from flask import Flask, request, jsonify, render_template
from serve import get_model_result
import sys
import time

app = Flask(__name__)

# model = get_model_result("안녕")

# result route
@app.route('/result', methods=['POST','GET'])
def result():
    value = request.form['input']
    result = get_model_result(value)
    return jsonify(result)

# default route
@app.route('/')
def index():
    return render_template('index.html')
def result():
    value = request.form['input']
    result = get_model_result(value)

    return result

# HTTP Errors handlers
@app.errorhandler(404)
def url_error(e):
    return """
    Wrong URL!
    <pre>{}</pre>""".format(e), 404

@app.errorhandler(500)
def server_error(e):
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500