from flask import Flask
from flask_mysqldb import MySQL
from .extensions import mysql



def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'NguyenHuy30'
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'flask_recog'

    mysql.init_app(app)

    from .views import views
    from .auth import auth
    from .process_img import process_img

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(process_img, url_prefix='/')

    return app