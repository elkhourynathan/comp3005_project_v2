from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, UserMixin, current_user
from dotenv import load_dotenv
import os
from flask_sqlalchemy import SQLAlchemy
from .models import Member, Trainer, Admin
from .database import db


# create flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'comp3005'

# Load environment variables
load_dotenv()


# Database information
DATABASE = os.getenv('MYAPP_DATABASE')
USER = os.getenv('MYAPP_USER')
PASSWORD = os.getenv('MYAPP_PASSWORD')
HOST = os.getenv('MYAPP_HOST')
PORT = os.getenv('MYAPP_PORT')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}'
db.init_app(app)


# Initialize routes
from .views import views
from .auth import auth
from .member import member
from .trainer import trainer
from .admin import admin


app.register_blueprint(views, url_prefix='/')
app.register_blueprint(auth, url_prefix='/')
app.register_blueprint(member, url_prefix='/')
app.register_blueprint(trainer, url_prefix='/')
app.register_blueprint(admin, url_prefix='/')


# Initialize Login Manager

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(username):
    user = Member.query.filter_by(username=username).first()
    if not user:
        user = Trainer.query.filter_by(username=username).first()
    if not user:
        user = Admin.query.filter_by(username=username).first()
    return user

if __name__ == '__main__':
    app.run(port=8000, debug=True)