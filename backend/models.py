from .database import db
from flask_login import UserMixin

class Member(db.Model, UserMixin):
    __tablename__ = 'member'
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
    
    # Relationships
    routines = db.relationship('Routine', backref='member')
    sessions = db.relationship('Sessions', backref='member')
    bills = db.relationship('Bill', backref='member')
    classes = db.relationship('MemberClasses', backref='member')

    def get_id(self):
        return self.username

class Routine(db.Model):
    __tablename__ = 'routine'
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    type = db.Column(db.String(255))
    date = db.Column(db.Date)

class Trainer(db.Model, UserMixin):
    __tablename__ = 'trainer'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    name = db.Column(db.String(255))
    
    # Relationships
    availabilities = db.relationship('Availability', backref='trainer')
    classes = db.relationship('Classes', secondary='availability', viewonly=True)

    def get_id(self):
        return self.username

class Availability(db.Model):
    __tablename__ = 'availability'
    id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainer.id'))
    available_start = db.Column(db.DateTime)
    available_end = db.Column(db.DateTime)
    open = db.Column(db.Boolean)
    
    # Relationships
    sessions = db.relationship('Sessions', backref='availability')
    classes = db.relationship('Classes', backref='availability')

class Admin(db.Model, UserMixin):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    name = db.Column(db.String(255))

    def get_id(self):
        return self.username
    
class Room(db.Model):
    __tablename__ = 'room'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

class Classes(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    availability_id = db.Column(db.Integer, db.ForeignKey('availability.id'))
    name = db.Column(db.String(255))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    
    # Relationships
    members = db.relationship('MemberClasses', backref='classes')

class MemberClasses(db.Model):
    __tablename__ = 'member_classes'
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), primary_key=True)

class Sessions(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    availability_id = db.Column(db.Integer, db.ForeignKey('availability.id'))

class Equipment(db.Model):
    __tablename__ = 'equipment'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(255))
    last_maintained = db.Column(db.DateTime)
    next_maintenance = db.Column(db.DateTime)

class Bill(db.Model):
    __tablename__ = 'bill'
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    amount = db.Column(db.Numeric(10, 2))
    paid = db.Column(db.Boolean)
    type = db.Column(db.String(255))
    date = db.Column(db.DateTime)