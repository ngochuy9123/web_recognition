from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'NguyenHuy30'

    from .views import views
    from .auth import auth
    from .process_img import process_img

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(process_img, url_prefix='/')

    return app