from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, UserMixin, current_user
from flask_sqlalchemy import SQLAlchemy
from .models import Member, Trainer, Admin
from .database import db


# create flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'comp3005'


# Database information
DATABASE = 'nek_project_v2'
USER = 'postgres'
PASSWORD = '1699'
HOST = 'localhost'
PORT = '5432'

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}'
db.init_app(app)


# Initialize routes
from .views import views
from .auth import auth

app.register_blueprint(views, url_prefix='/')
app.register_blueprint(auth, url_prefix='/')


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