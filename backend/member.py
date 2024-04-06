from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps
from .database import db
from .models import Member, Trainer, Admin, Availability, Classes, Sessions, Bill, MemberClasses,Routine, Equipment
from .views import member_required

member = Blueprint('member', __name__)

# Member related routes

@member.route('/member_home/profile', methods=['GET', 'POST'])
@login_required
@member_required
def member_profile():
    current_user.is_member = True
    return render_template('member_profile.html', user=current_user)

@member.route('/member_home', methods=['GET', 'POST'])
@login_required
@member_required
def member_home():
    # Add trait to user that is member
    current_user.is_member = True

    # Get routines
    routines = Routine.query.filter_by(member_id=current_user.id).all()

    one_week_ago = (datetime.now() - timedelta(days=7)).date()

    workouts_in_last_week = len([routine for routine in routines if routine.date >= one_week_ago])


    return render_template("member_home.html", 
                           user=current_user, 
                           routines=routines,
                           workouts_in_last_week=workouts_in_last_week)

@member.route('/member_home/update_routine', methods=['POST'])
@login_required
@member_required
def update_routine():
    type = request.form.get('routine_type')
    date = request.form.get('routine_date')

    if not type or not date:
        flash('While editing routine ensure fields are filled.', category='error')

    new_routine = Routine(member_id=current_user.id, type=type, date=date)
    db.session.add(new_routine)
    db.session.commit()

    flash('Routine updated', category='success')
    return redirect(url_for('member.member_home'))

@member.route('/member_home/add_routine', methods=['POST'])
@login_required
@member_required
def add_routine():
    type = request.form.get('new_routine_type')
    date = request.form.get('new_routine_date')
    
    print(type, date)
    if not type or not date:
        flash('Please fill out all fields', category='error')
        return redirect(url_for('member.member_home'))


    new_routine = Routine(member_id=current_user.id, type=type, date=date)
    db.session.add(new_routine)
    db.session.commit()

    flash('Routine added', category='success')
    return redirect(url_for('member.member_home'))

@member.route('/member_home/delete_routine/<routine_id>', methods=['POST'])
@login_required
@member_required
def delete_routine(routine_id):
    routine = Routine.query.get(routine_id)
    if routine:
        db.session.delete(routine)
        db.session.commit()

    flash('Routine deleted', category='success')
    return redirect(url_for('member.member_home'))

@member.route('/member_home/scheduling', methods=['GET', 'POST'])
@login_required
@member_required
def member_home_scheduling():
    # Add trait to user that is member
    current_user.is_member = True

    # Traier availabilities
    availabilities = Availability.query.all()

    # Query based off the availability trainer_id name to get the matching trainer name from Trainers
    for availability in availabilities:
        trainer = Trainer.query.filter_by(id=availability.trainer_id).first()
        availability.trainer_name = trainer.name

    # Class schedules
    classes = Classes.query.all()

    # Query Sessions and filter by member_id
    sessions = Sessions.query.filter_by(member_id=current_user.id).all()

    # Query based off the session trainer_id name to get the matching trainer name from Trainers
    for session in sessions:
        trainer = Trainer.query.filter_by(id=session.trainer_id).first()
        session.trainer_name = trainer.name

    # Query MemberClasses for all classes that the current user is booked for
    member_classes = MemberClasses.query.filter_by(member_id=current_user.id).all()

    member_class_ids = [mc.class_id for mc in member_classes]

    # Query Classes for all classes that the current user is booked for
    booked_classes = Classes.query.filter(Classes.id.in_(member_class_ids)).all()

    # Sort all lists by id
    availabilities.sort(key=lambda x: x.id)
    classes.sort(key=lambda x: x.id)
    sessions.sort(key=lambda x: x.id)
    booked_classes.sort(key=lambda x: x.id)


    return render_template("member_home_scheduling.html", 
                           user=current_user, 
                           availabilities=availabilities, 
                           classes=classes, sessions=sessions, 
                           booked_classes=booked_classes)

@member.route('/member_home/update_profile', methods=['POST'])
@login_required
@member_required
def update_profile():
    name = request.form.get('name')
    profile_info = request.form.get('profile_info')
    fitness_goals = request.form.get('fitness_goals')
    health_metrics = request.form.get('health_metrics')
    height = request.form.get('height')
    weight = request.form.get('weight')
    goal_weight = request.form.get('goal_weight')
    goal_workouts_per_week = request.form.get('goal_workouts_per_week')

    if (not name 
        or not profile_info 
        or not fitness_goals 
        or not health_metrics 
        or not height 
        or not weight 
        or not goal_weight 
        or not goal_workouts_per_week):
        flash('Please fill out all fields', category='error')
        return redirect(url_for('member.member_profile'))

    current_user.name = name
    current_user.profile_info = profile_info
    current_user.fitness_goals = fitness_goals
    current_user.health_metrics = health_metrics
    current_user.height = height
    current_user.weight = weight
    current_user.goal_weight = goal_weight
    current_user.goal_workouts_per_week = goal_workouts_per_week

    db.session.commit()

    return redirect(url_for('member.member_profile'))


@member.route('/member_home/book_session', methods=['POST'])
@login_required
@member_required
def book_session():
    user_id = current_user.id
    trainer_id = request.form.get('trainer_id')

    # remove the letter T
    date = request.form.get('session_date').strip().replace('T', ' ')
    date_time = date + ':00'
    credit_card_number = request.form.get('session_credit_card_number')
    if not credit_card_number:
        flash('Please enter a valid credit card number', category='error')

    # check if date_time is valid format for datetime
    try:
        date_time = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        flash('Invalid date format', category='error')
        return redirect(url_for('member.member_home_scheduling'))
    

    # Remove from availabilities tuple with the same trainer id and start time
    availability = Availability.query.filter_by(trainer_id=trainer_id, available_start=date_time).first()
    if not availability:
        flash('Trainer is not available at that time', category='error')
        return redirect(url_for('member.member_home_scheduling'))
    db.session.delete(availability)
    db.session.commit()


    # Create new bill
    bill = Bill(member_id=user_id, amount=50.00, date=datetime.today(), paid=True, type="Session")
    db.session.add(bill)
    db.session.commit()
    # Add new session to sessions table

    new_session = Sessions(member_id=user_id, trainer_id=trainer_id, date_time=date_time)
    db.session.add(new_session)
    db.session.commit()
    
    flash('Session booked and billing accepted!', category='success')
    return redirect(url_for('member.member_home_scheduling'))


@member.route('/member_home/reschedule_session/<original_session_id>', methods=['POST'])
@login_required
@member_required
def reschedule_session(original_session_id):

    new_trainer_id = request.form.get('session_trainer_id')
    new_start_time = request.form.get('session_date_time')

    print(new_start_time, new_trainer_id)
    new_start_time = datetime.strptime(new_start_time, '%Y-%m-%dT%H:%M')

    # Check if a reschedule is possible
    availability = Availability.query.filter_by(trainer_id=new_trainer_id, available_start=new_start_time).first()

    if availability:
        # Get the original session
        session = Sessions.query.get(original_session_id)

        if session:
            # Re-add the original session back to Availability
            available_end = session.date_time + timedelta(hours=1)
            original_availability = Availability(trainer_id=session.trainer_id, available_start=session.date_time, available_end=available_end)
            db.session.add(original_availability)

            # Update to match the new session booked
            session.trainer_id = new_trainer_id
            session.date_time = new_start_time

            # Remove the availability
            db.session.delete(availability)
            
            db.session.commit()

            flash('Session rescheduled', category='success')
        else:
            flash('Session not found', category='error')
    else:
        flash('Availability not found', category='error')

    return redirect(url_for('member.member_home_scheduling'))

@member.route('/member_home/delete_session/<session_id>', methods=['POST'])
@login_required
@member_required
def delete_session(session_id):
    new_available_start = request.form.get('new_available_start')
    new_available_end = request.form.get('new_available_end')

    if new_available_start and new_available_end:
        new_available_start = datetime.strptime(new_available_start, '%Y-%m-%dT%H:%M')
        new_available_end = datetime.strptime(new_available_end, '%Y-%m-%dT%H:%M')
        new_availability = Availability(trainer_id=current_user.id, available_start=new_available_start, available_end=new_available_end)
        db.session.add(new_availability)
        db.session.commit()

    session = Sessions.query.get(session_id)
    session_trainer_id = request.form.get('session_trainer_id')
    session_date_time = request.form.get('session_date_time')
    if session:
        db.session.delete(session)


        # Re-add availability
        available_start = datetime.strptime(session_date_time, '%Y-%m-%dT%H:%M')
        available_end = available_start + timedelta(hours=1)
        new_availability = Availability(trainer_id=session_trainer_id, available_start=available_start, available_end=available_end)
        db.session.add(new_availability)
        db.session.commit()
    
    refund = Bill(member_id=current_user.id, amount=-50.00, date=datetime.today(), paid=True, type="Session")
    db.session.add(refund)
    db.session.commit()

    flash('Session removed', category='success')
    return redirect(url_for('member.member_home_scheduling'))


@member.route('/member_home/delete_class', methods=['POST'])
@login_required
@member_required
def delete_class():
    class_id = request.form.get('class_id')
    class_relationship = MemberClasses.query.filter_by(class_id=class_id, member_id=current_user.id).first()
    if class_relationship:
        db.session.delete(class_relationship)
        db.session.commit()

    refund = Bill(member_id=current_user.id, amount=-100.00, date=datetime.today(), paid=True, type="Class")
    db.session.add(refund)
    db.session.commit()

    flash('Class booking removed', category='success')
    return redirect(url_for('member.member_home_scheduling'))

@member.route('/member_home/book_class', methods=['POST'])
@login_required
@member_required
def book_class():
    user_id = current_user.id
    class_name = request.form.get('class_name')
    
    class_time = request.form.get('class_time').strip().replace('T', ' ') + ':00'
    credit_card_number = request.form.get('class_credit_card_number')


    # Credit card number validation
    if not credit_card_number:
        flash('Please enter a valid credit card number', category='error')
        return redirect(url_for('member.member_home_scheduling'))

    # check if class_time is valid format for datetime
    try:
        class_time = datetime.strptime(class_time, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        flash('Please ensure your entering a valid time', category='error')
        return redirect(url_for('member.member_home_scheduling'))

    # Query the class with the same name and time
    class_ = Classes.query.filter(Classes.name.like(f"%{class_name}%"), Classes.schedule == class_time).first()
    if not class_:
        flash('Could not find class', category='error')
        return redirect(url_for('member.member_home_scheduling'))

    # Check if user already booked for class
    member_class = MemberClasses.query.filter_by(member_id=user_id, class_id=class_.id).first()
    if member_class:
        flash('You are already booked for this class', category='error')
        return redirect(url_for('member.member_home_scheduling'))

    # Create new bill
    bill = Bill(member_id=user_id, amount=50.00, date=datetime.today(), paid=True, type="Class")
    db.session.add(bill)
    db.session.commit()

    # Add new member class to MemberClasses table
    new_member_class = MemberClasses(member_id=user_id, class_id=class_.id)
    db.session.add(new_member_class)
    db.session.commit()

    flash('Class booked and billing accepted!', category='success')
    return redirect(url_for('member.member_home_scheduling'))
    
