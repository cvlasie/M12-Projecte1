from flask import Flask, render_template
import sqlite3
from flask import g

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<h1>Pagina Principal!</h1>"

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)

def get_product_list():
    conn = sqlite3.connect('M12-Practica01.db') 
    cursor = conn.cursor()
    cursor.execute('SELECT title, description, photo, price FROM products')
    products = cursor.fetchall()
    conn.close()
    return products

@app.route('/products/list')
def list_products():
    products = get_product_list()
    return render_template('list.html', products=products)