from flask import Flask, render_template, request, flash, redirect, url_for, g
import sqlite3
from datetime import datetime

app = Flask(__name__)

# SECRET_KEY: clau d'encriptació de la cookie
app.config.update(
    SECRET_KEY='secret_xxx'
)

# Función para obtener la lista de productos
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('M12-Practica01.db')
    return db

@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def get_product_list():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT title, description, photo, price FROM products')
    products = cursor.fetchall()
    return products

@app.route("/")
def hello_world():
    return "<h1>Página Principal!</h1>"

@app.route('/gracias')
def gracias():
    return render_template('gracias.html')

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)

@app.route('/products/list')
def list_products():
    products = get_product_list()
    return render_template('list.html', products=products)

@app.route('/products/create', methods=["GET", "POST"])
def resource_create():
    if request.method == 'POST':
        # Obtén los datos del formulario
        title = request.form.get("title")
        description = request.form.get("description")
        photo = request.form.get("photo")
        price = request.form.get("price")
        
        # Obtiene la fecha y hora actual
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Inserta los datos en la base de datos y guarda la fecha de creación
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO products (title, description, photo, price, created, updated)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, description, photo, price, current_datetime, current_datetime))
        
        # Commit para guardar los cambios en la base de datos
        db.commit()
        
        # Obtén el ID del producto recién registrado
        cursor.execute("SELECT last_insert_rowid()")
        product_id = cursor.fetchone()[0]

        # Cierra el cursor
        cursor.close()
        
        return redirect(url_for('gracias'))
    return render_template('create.html')

if __name__ == '__main__':
    app.run()