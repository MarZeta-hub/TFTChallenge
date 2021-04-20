from flask import Flask
from flask_login import LoginManager
from src.crud import CRUDUser
from flask_sslify import SSLify
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    @login_manager.user_loader
    def load_user(user):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return CRUDUser().loginUser(user)

    return app

    if 'DYNO' in os.environ: # only trigger SSLify if the app is running on Heroku
        sslify = SSLify(app)


