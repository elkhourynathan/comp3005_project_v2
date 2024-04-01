from flask_sqlalchemy import SQLAlchemy

# Database information
DATABASE = 'nek_project_v1'
USER = 'postgres'
PASSWORD = '1699'
HOST = 'localhost'
PORT = '5432'


db = SQLAlchemy()