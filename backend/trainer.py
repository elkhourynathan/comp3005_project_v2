from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps
from .database import db
from .models import Member, Trainer, Admin, Availability, Classes, Sessions, Bill, MemberClasses,Routine, Equipment
from .views import trainer_required

trainer = Blueprint('trainer', __name__)


# Trainer related routes

@trainer.route('/trainer_home', methods=['GET', 'POST'])
@login_required
@trainer_required
def trainer_home():
    availabilities = Availability.query.filter_by(trainer_id=current_user.id).all()
    for availability in availabilities:
        trainer = Trainer.query.filter_by(id=availability.trainer_id).first()
        availability.trainer_name = trainer.name
    
    sessions = Sessions.query.filter_by(trainer_id=current_user.id).all()
    for session in sessions:
        member = Member.query.filter_by(id=session.member_id).first()
        trainer = Trainer.query.filter_by(id=session.trainer_id).first()
        session.member_name = member.name
        session.trainer_name = trainer.name
    
    members = Member.query.all()
    
    # Sorting
    members.sort(key=lambda x: x.id)
    sessions.sort(key=lambda x: x.id)
    availabilities.sort(key=lambda x: x.id)

    return render_template("trainer_home.html", 
                           user=current_user, 
                           members=members, 
                           availabilities=availabilities, 
                           sessions=sessions)

@trainer.route('/trainer_home/member_filter', methods=['GET'])
@login_required
@trainer_required
def member_filter():
    availabilities = Availability.query.filter_by(trainer_id=current_user.id).all()
    for availability in availabilities:
        trainer = Trainer.query.filter_by(id=availability.trainer_id).first()
        availability.trainer_name = trainer.name

    sessions = Sessions.query.filter_by(trainer_id=current_user.id).all()
    for session in sessions:
        member = Member.query.filter_by(id=session.member_id).first()
        trainer = Trainer.query.filter_by(id=session.trainer_id).first()
        session.member_name = member.name
        session.trainer_name = trainer.name

    search = request.args.get('search')
    members = Member.query.filter(Member.username.ilike(f'%{search}%')).all()
    return render_template("trainer_home.html", 
                           user=current_user, 
                           members=members, 
                           availabilities=availabilities,
                           sessions=sessions)

@trainer.route('/trainer_home/update_availability', methods=['POST'])
@login_required
@trainer_required
def update_availability():
    available_starts = request.form.getlist('available_start')
    available_ends = request.form.getlist('available_end')
    availabilities = Availability.query.filter_by(trainer_id=current_user.id).all()

    for i, availability in enumerate(availabilities):
        availability.available_start = datetime.strptime(available_starts[i], '%Y-%m-%dT%H:%M')
        availability.available_end = datetime.strptime(available_ends[i], '%Y-%m-%dT%H:%M')

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
    new_available_end = request.form.get('new_available_end')

    if new_available_start and new_available_end:
        new_available_start = datetime.strptime(new_available_start, '%Y-%m-%dT%H:%M')
        new_available_end = datetime.strptime(new_available_end, '%Y-%m-%dT%H:%M')
        new_availability = Availability(trainer_id=current_user.id, available_start=new_available_start, available_end=new_available_end)
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
        db.session.delete(session)
        db.session.commit()

    refund = Bill(member_id=session.member_id, amount=-50.00, date=datetime.today(), paid=True, type="Session")
    db.session.add(refund)
    db.session.commit()

    flash('Session deleted', category='success')
    return redirect(url_for('trainer.trainer_home'))
