from flask import Flask, render_template, request, flash, redirect, url_for, g
import sqlite3
from flask import send_from_directory
from datetime import datetime
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# SECRET_KEY: clau d'encriptació de la cookie
app.config.update(
    SECRET_KEY='secret_xxx',
    UPLOAD_FOLDER='upload'  # Carpeta de carga de archivos
)

# Función para obtener la lista de productos
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('M12-Practica01.db')
    return db

def get_product_list():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id, title, description, photo, price FROM products')
    products = cursor.fetchall()
    return products

def get_product_by_id(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT title, description, photo, price FROM products WHERE id = ?', (id,))
    product = cursor.fetchone()
    return product

# Función para verificar la extensión del archivo
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png', 'gif'}

@app.route("/")
def index():
    return render_template('index.html')

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
        
        # Verifica si se ha proporcionado un archivo
        if 'photo' in request.files:
            photo = request.files['photo']
            
            # Verifica si el archivo tiene un nombre y es una extensión de archivo permitida
            if photo.filename != '' and allowed_file(photo.filename):
                # Genera un nombre seguro para el archivo
                filename = secure_filename(photo.filename)
                
                # Guarda el archivo en la carpeta de carga
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                flash('Formato de archivo no válido', 'error')
                return redirect(url_for('resource_create'))
        else:
            flash('No se ha proporcionado un archivo', 'error')
            return redirect(url_for('resource_create'))
        
        # Obtén el precio del formulario
        price = request.form.get("price")
        
        # Obtiene la fecha y hora actual
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Inserta los datos en la base de datos y guarda la fecha de creación
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO products (title, description, photo, price, created, updated)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, description, filename, price, current_datetime, current_datetime))
        
        # Commit para guardar los cambios en la base de datos
        db.commit()
        
        # Obtén el ID del producto recién registrado
        cursor.execute("SELECT last_insert_rowid()")
        product_id = cursor.fetchone()[0]

        # Cierra el cursor
        cursor.close()
        
        return redirect(url_for('gracias'))
    return render_template('create.html')

@app.route('/products/read/<int:id>')
def product_read(id):
    product = get_product_by_id(id)
    if product is None:
        flash('Producto no encontrado', 'error')
        return redirect(url_for('list_products'))
    return render_template('read.html', product=product)

@app.route('/products/update/<int:id>', methods=["GET", "POST"])
def products_update(id):
    if request.method == 'GET':
        # Obtén los datos del producto de la base de datos SQLite
        product = get_product_by_id(id)
        
        if product is None:
            flash('Producto no encontrado', 'error')
            return redirect(url_for('list_products'))
        
        # Muestra los datos del producto en el formulario de actualización
        return render_template('update.html', product_id=id, product=product)  # Pasamos el id como product_id en la respuesta
    
    elif request.method == 'POST':
        # Obtén los datos del formulario
        title = request.form.get("title")
        description = request.form.get("description")
        
        # Verifica si se ha proporcionado un archivo
        if 'photo' in request.files:
            photo = request.files['photo']
            
            # Verifica si el archivo tiene un nombre y es una extensión de archivo permitida
            if photo.filename != '' and allowed_file(photo.filename):
                # Genera un nombre seguro para el archivo
                filename = secure_filename(photo.filename)
                
                # Guarda el archivo en la carpeta de carga
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                flash('Formato de archivo no válido', 'error')
                return redirect(url_for('products_update', id=id))
        else:
            flash('No se ha proporcionado un archivo', 'error')
            return redirect(url_for('products_update', id=id))
        
        # Obtén el precio del formulario
        price = request.form.get("price")
        
        # Actualiza los datos del producto en la base de datos SQLite
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            UPDATE products
            SET title=?, description=?, photo=?, price=?
            WHERE id=?
        ''', (title, description, filename, price, id))
        
        # Commit para guardar los cambios en la base de datos
        db.commit()
        
        return redirect(url_for('list_products'))

@app.route('/products/delete/<int:id>', methods=["GET", "POST"])
def products_delete(id):
    if request.method == 'GET':
        # Obtén los datos del producto de la base de datos SQLite
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id, title, description, photo, price FROM products WHERE id = ?', (id,))
        product = cursor.fetchone()

        if product is None:
            flash('Producto no encontrado', 'error')
            return redirect(url_for('list_products'))

        # Muestra los datos del producto en la página de eliminación
        return render_template('delete.html', resource=product)

    elif request.method == 'POST':
        # Elimina el producto de la base de datos SQLite
        db = get_db()
        cursor = db.cursor()
        cursor.execute('DELETE FROM products WHERE id = ?', (id,))
        db.commit()

        return redirect(url_for('list_products'))

if __name__ == '__main__':
    app.run()