from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# ruta absoluta d'aquesta carpeta
basedir = os.path.abspath(os.path.dirname(__file__)) 

# Configuración de la base de datos SQLite usando SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + basedir + "/M12-Practica01.db"
db = SQLAlchemy(app)

# Configuración adicional
app.config['SECRET_KEY'] = 'secret_xxx'
app.config['UPLOAD_FOLDER'] = 'upload'

# Definición del modelo Product
class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    photo = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Float, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Función para obtener la lista de productos
def get_product_list():
    products = Product.query.with_entities(Product.id, Product.title, Product.description, Product.photo, Product.price).all()
    return products

# Función para obtener un producto por su ID
def get_product_by_id(id):
    product = Product.query.filter_by(id=id).first()
    if product:
        return product.title, product.description, product.photo, product.price
    return None

# Función para verificar la extensión del archivo
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png', 'gif'}

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

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
        
        # Crea un nuevo producto en la base de datos
        new_product = Product(
            title=title,
            description=description,
            photo=filename,
            price=price
        )
        db.session.add(new_product)
        db.session.commit()
        
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
    product = Product.query.get(id)
    
    if product is None:
        flash('Producto no encontrado', 'error')
        return redirect(url_for('list_products'))
    
    if request.method == 'POST':
        # Obtén los datos del formulario
        title = request.form.get("title")
        description = request.form.get("description")
        price = request.form.get("price")
        
        # Obtén el archivo de imagen cargado
        photo = request.files.get("photo")
        
        # Verifica si se cargó una nueva imagen y procesa si es necesario
        if photo:
            # Guarda la nueva imagen en la carpeta de carga de archivos
            photo_filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
            
            # Actualiza los datos del producto
            product.title = title
            product.description = description
            product.photo = photo_filename
            product.price = price
        else:
            # Si no se cargó una nueva imagen, actualiza los otros campos
            product.title = title
            product.description = description
            product.price = price

        # Actualiza la fecha de actualización
        product.updated = datetime.utcnow()

        # Guarda los cambios en la base de datos
        db.session.commit()

        return redirect(url_for('list_products'))
    
    return render_template('update.html', product=product)


@app.route('/products/delete/<int:id>', methods=["GET", "POST"])
def products_delete(id):
    product = Product.query.get(id)
    
    if product is None:
        flash('Producto no encontrado', 'error')
        return redirect(url_for('list_products'))
    
    if request.method == 'POST':
        # Elimina el producto de la base de datos
        db.session.delete(product)
        db.session.commit()

        return redirect(url_for('list_products'))
    
    return render_template('delete.html', resource=product)

if __name__ == '__main__':
    app.run(debug=True, use_debugger=False, use_reloader=False)