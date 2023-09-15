from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<h1>Pagina Principal!</h1>"

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)