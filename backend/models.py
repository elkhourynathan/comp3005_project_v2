from .database import db
from flask_login import UserMixin

class Member(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    name = db.Column(db.String(255))
    profile_info = db.Column(db.Text)
    fitness_goals = db.Column(db.Text)
    health_metrics = db.Column(db.Text)
    height = db.Column(db.Numeric(5, 2))
    weight = db.Column(db.Numeric(5, 2))
    goal_weight = db.Column(db.Numeric(5, 2))
    goal_workouts_per_week = db.Column(db.Integer)

    def get_id(self):
        return self.username

class Routine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    type = db.Column(db.String(255))
    date = db.Column(db.Date)

class Trainer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    name = db.Column(db.String(255))
    schedule = db.Column(db.Text)

    def get_id(self):
        return self.username

class Availability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainer.id'))
    available_start = db.Column(db.DateTime)
    available_end = db.Column(db.DateTime)

class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    name = db.Column(db.String(255))
    def get_id(self):
        return self.username

class Classes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    room = db.Column(db.String(255))
    schedule = db.Column(db.DateTime)

class Sessions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainer.id'))
    date_time = db.Column(db.DateTime)

class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(255))
    maintenance_schedule = db.Column(db.DateTime)

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    amount = db.Column(db.Numeric(10, 2))
    date = db.Column(db.DateTime)