from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps
from .database import db
from .models import Member, Trainer, Availability, Classes, Sessions, Bill, MemberClasses, Room
from .views import trainer_required

trainer = Blueprint('trainer', __name__)


# Trainer related routes

@trainer.route('/trainer_home', methods=['GET', 'POST'])
@login_required
@trainer_required
def trainer_home():

    availabilities = db.session.query(
        Availability.id.label("id"),
        Availability.trainer_id.label("trainer_id"),
        Availability.available_start.label("available_start"),
        Availability.available_end.label("available_end"),
        Trainer.name.label("trainer_name")
        ).join(Trainer, Availability.trainer_id == Trainer.id) \
        .filter(Availability.trainer_id == current_user.id).all()
    
    sessions = db.session.query(
        Sessions.id.label("id"),
        Member.id.label("member_id"),
        Member.name.label("member_name"),
        Trainer.id.label("trainer_id"),
        Trainer.name.label("trainer_name"),
        Availability.available_start.label("date_time")
    ).join(Availability, Sessions.availability_id == Availability.id) \
     .join(Member, Sessions.member_id == Member.id) \
     .join(Trainer, Availability.trainer_id == Trainer.id) \
     .filter(Availability.trainer_id == current_user.id).all()
    
    classes = db.session.query(
        Classes.id.label("id"),
        Classes.name.label("name"),
        Room.name.label("room"),
        Availability.available_start.label("start_time")
    ).join(Availability, Classes.availability_id == Availability.id) \
        .join(Room, Classes.room_id == Room.id) \
            .filter(Availability.trainer_id == current_user.id).all()


    members = Member.query.all()
    members.sort(key=lambda x: x.id)
    sessions.sort(key=lambda x: x.id)
    availabilities.sort(key=lambda x: x.available_start, reverse=True)
    classes.sort(key=lambda x: x.start_time, reverse=True)

    return render_template("trainer_home.html", 
                           user=current_user, 
                           members=members, 
                           availabilities=availabilities, 
                           sessions=sessions,
                           classes=classes)

@trainer.route('/trainer_home/member_filter', methods=['GET'])
@login_required
@trainer_required
def member_filter():

    availabilities = db.session.query(
        Availability.id.label("id"),
        Availability.trainer_id.label("trainer_id"),
        Availability.available_start.label("available_start"),
        Availability.available_end.label("available_end"),
        Trainer.name.label("trainer_name")
        ).join(Trainer, Availability.trainer_id == Trainer.id) \
        .filter(Availability.trainer_id == current_user.id).all()
    
    sessions = db.session.query(
        Sessions.id.label("id"),
        Member.id.label("member_id"),
        Member.name.label("member_name"),
        Trainer.id.label("trainer_id"),
        Trainer.name.label("trainer_name"),
        Availability.available_start.label("date_time")
    ).join(Availability, Sessions.availability_id == Availability.id) \
     .join(Member, Sessions.member_id == Member.id) \
     .join(Trainer, Availability.trainer_id == Trainer.id) \
     .filter(Availability.trainer_id == current_user.id).all()
    
    classes = db.session.query(
        Classes.id.label("id"),
        Classes.name.label("name"),
        Room.name.label("room"),
        Availability.available_start.label("start_time")
    ).join(Availability, Classes.availability_id == Availability.id) \
        .join(Room, Classes.room_id == Room.id) \
            .filter(Availability.trainer_id == current_user.id).all()
            

    search = request.args.get('search')
    members = Member.query.filter(Member.username.ilike(f'%{search}%')).all()
    members.sort(key=lambda x: x.id)
    sessions.sort(key=lambda x: x.id)
    availabilities.sort(key=lambda x: x.available_start)
    classes.sort(key=lambda x: x.start_time, reverse=True)

    return render_template("trainer_home.html", 
                           user=current_user, 
                           members=members, 
                           availabilities=availabilities,
                           sessions=sessions,
                           classes=classes)

@trainer.route('/trainer_home/update_availability/<availability_id>', methods=['POST'])
@login_required
@trainer_required
def update_availability(availability_id):
    updated_start = datetime.strptime(request.form.get('available_start'), '%Y-%m-%dT%H:%M')
    availability = Availability.query.get(availability_id)

    prev_availability = Availability.query.filter_by(trainer_id=current_user.id, available_start=updated_start).first()

    print(updated_start)
    print(prev_availability)
    if prev_availability:
        print(prev_availability.id, availability.id, prev_availability.available_start, availability.available_start, prev_availability.available_start == availability.available_start)
        flash('Availability already exists', category='error')
        return redirect(url_for('trainer.trainer_home'))
    else:
        availability.available_start = updated_start
        availability.available_end = updated_start + timedelta(hours=1)

    db.session.commit()

    flash('Availability updated', category='success')
    return redirect(url_for('trainer.trainer_home'))

@trainer.route('/trainer_home/delete_availability/<availability_id>', methods=['POST'])
@login_required
@trainer_required
def delete_availability(availability_id):
    availability = Availability.query.get(availability_id)
    if availability:
        db.session.delete(availability)
        db.session.commit()

    flash('Availability deleted', category='success')
    return redirect(url_for('trainer.trainer_home'))

@trainer.route('/trainer_home/add_availability', methods=['POST'])
@login_required
@trainer_required
def add_availability():
    new_available_start = request.form.get('new_available_start')

    if new_available_start:
        # Check that this availability doesnt already exist
        new_available_start = datetime.strptime(new_available_start, '%Y-%m-%dT%H:%M')
        pre_existing = Availability.query.filter_by(trainer_id=current_user.id, available_start=new_available_start).first()
        if pre_existing:
            flash('Availability already exists', category='error')
            return redirect(url_for('trainer.trainer_home'))
        
        new_available_end = new_available_start + timedelta(hours=1)
        new_availability = Availability(trainer_id=current_user.id, available_start=new_available_start, available_end=new_available_end, open=True)
        db.session.add(new_availability)
        db.session.commit()

    flash('Availability added', category='success')
    return redirect(url_for('trainer.trainer_home'))


@trainer.route('/trainer_home/delete_session/<session_id>', methods=['POST'])
@login_required
@trainer_required
def trainer_delete_session(session_id):

    session = Sessions.query.get(session_id)
    if session:
        refund = Bill(member_id=session.member_id, amount=-50.00, date=datetime.today(), paid=True, type="Session")
        db.session.add(refund)
        
        availability = Availability.query.get(session.availability_id)


        db.session.delete(availability)
        db.session.delete(session)
        db.session.commit()

        flash('Session deleted', category='success')
    else:
        flash('Session not found', category='error')
    return redirect(url_for('trainer.trainer_home'))


@trainer.route('/trainer_home/delete_class/<class_id>', methods=['POST'])
@login_required
@trainer_required
def delete_class(class_id):
    # get the class
    class_ = Classes.query.get(class_id)

    # Refund all members
    members = MemberClasses.query.filter_by(class_id=class_.id).all()
    for member in members:
        refund = Bill(member_id=member.member_id, amount=-100.00, date=datetime.today(), paid=True, type="Class")
        db.session.add(refund)
        db.session.delete(member)
        db.session.commit()
    

    # delete the class and availability
    availability = Availability.query.get(class_.availability_id)

    db.session.delete(availability)
    db.session.delete(class_)
    db.session.commit()

    flash('Class deleted and members refunded', category='success')
    return redirect(url_for('trainer.trainer_home'))
    