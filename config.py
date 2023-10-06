import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))

class Config:
    # Carrega les variables del fitxer .env
    
    FLASK_APP = os.environ.get("FLASK_APP")
    FLASK_DEBUG = os.environ.get("FLASK_DEBUG")
    SECRET_KEY = os.environ.get("SECRET_KEY")

    # Altres variables definides directament en el codi
    STATIC_FOLDER = "static"
    TEMPLATES_FOLDER = "templates"

    # Fitxer amb la base de dades
    SQLITE3_DATABASE_PATH = os.path.join(basedir, "M12-Practica01.db")

    # Cadena de connexió de SQLAlchemy
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + SQLITE3_DATABASE_PATH