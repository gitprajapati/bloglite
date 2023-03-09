from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'TOPsecretcadewgtrrjuuyjkimujadadadfagfagAGAGDFvafaFARFACSDVaferFasfFvaFVAf'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
    app.config['SECURITY_PASSWORD_SALT'] = "kjcfslijfcklsejfisjfisejfvilesjfivhsefuhseiflakjcflajdliajfcisjvkdmbkdjg8eutigfvniLIDJAFJSILVJ"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    UPLOAD_FOLDER = app.root_path+'static\\'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    @app.errorhandler(404)
    def no_match(e):
        return render_template("404.html"), 404

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User

    database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Please login first to use this page."
    login_manager.login_message_category = "warning"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def database(app):
    if not path.exists('blog/database.sqlite3'):
        db.create_all(app=app)
