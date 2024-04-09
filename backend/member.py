from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .database import db
from .models import Trainer, Availability, Classes, Sessions, Bill, MemberClasses,Routine, Room
from .views import member_required

member = Blueprint('member', __name__)

# Member related routes

@member.route('/member_home/profile', methods=['GET', 'POST'])
@login_required
@member_required
def member_profile():
    current_user.is_member = True
    return render_template('member_profile.html', user=current_user)


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

    height = round(float(height), 2)
    weight = round(float(weight), 2)
    goal_weight = round(float(goal_weight), 2)
    goal_workouts_per_week = round(float(goal_workouts_per_week), 2)

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

@member.route('/member_home', methods=['GET', 'POST'])
@login_required
@member_required
def member_home():
    # Add trait to user that is member
    current_user.is_member = True

    # Get routines
    routines = Routine.query.filter_by(member_id=current_user.id).all()

    # Sort routines by date
    routines.sort(key=lambda x: x.date, reverse=True)

    one_week_ago = (datetime.now() - timedelta(days=7)).date()

    workouts_in_last_week = len([routine for routine in routines if routine.date >= one_week_ago])


    return render_template("member_home.html", 
                           user=current_user, 
                           routines=routines,
                           workouts_in_last_week=workouts_in_last_week)

@member.route('/member_home/update_routine/<routine_id>', methods=['POST'])
@login_required
@member_required
def update_routine(routine_id):
    type = request.form.get('routine_type')
    date = request.form.get('routine_date')
    date = datetime.strptime(date, '%Y-%m-%d')

    if not type or not date:
        flash('While editing routine ensure fields are filled.', category='error')

    routine = Routine.query.get(routine_id)
    print(routine.id, routine.member_id, routine.type, routine.date)
    if routine:
        routine.type = type
        routine.date = date
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

    # Trainer availabilities
    availabilities = db.session.query(
        Availability.id.label("id"),
        Availability.available_start.label("available_start"),
        Availability.available_end.label("available_end"),
        Trainer.name.label("trainer_name")
    ).join(Trainer, Availability.trainer_id == Trainer.id) \
     .filter(Availability.open == True).all()

    # Class schedules
    classes = db.session.query(
        Classes.id.label("id"),
        Classes.name.label("name"),
        Room.name.label("room"),
        Availability.available_start.label("start_time")
    ).join(Availability, Classes.availability_id == Availability.id) \
    .join(Room, Classes.room_id == Room.id).all()

    # Query Sessions and filter by member_id
    sessions = db.session.query(
        Sessions.id.label("id"),
        Trainer.id.label("trainer_id"),
        Trainer.name.label("trainer_name"),
        Availability.available_start.label("date_time")
    ).join(Availability, Sessions.availability_id == Availability.id) \
     .join(Trainer, Availability.trainer_id == Trainer.id) \
     .filter(Sessions.member_id == current_user.id).all()

    # Query MemberClasses for all classes that the current user is booked for
    member_classes = MemberClasses.query.filter_by(member_id=current_user.id).all()

    member_class_ids = [mc.class_id for mc in member_classes]

    # Query Classes for all classes that the current user is booked for
    booked_classes = db.session.query(
        Classes.id.label("id"),
        Classes.name.label("name"),
        Room.name.label("room"),
        Availability.available_start.label("start_time")
    ).join(Availability, Classes.availability_id == Availability.id) \
     .join(Room, Classes.room_id == Room.id) \
     .filter(Classes.id.in_(member_class_ids)).all()

    # Sort all lists by id
    availabilities.sort(key=lambda x: x.id)
    classes.sort(key=lambda x: x.id)
    sessions.sort(key=lambda x: x.id)
    booked_classes.sort(key=lambda x: x.id)

    return render_template("member_home_scheduling.html", 
                           user=current_user, 
                           availabilities=availabilities, 
                           classes=classes, 
                           sessions=sessions, 
                           booked_classes=booked_classes)


@member.route('/member_home/book_session', methods=['POST'])
@login_required
@member_required
def book_session():
    user_id = current_user.id
    availability_id = request.form.get('availability_id')
    credit_card_number = request.form.get('session_credit_card_number')
    if not credit_card_number:
        flash('Please enter a valid credit card number', category='error')
        return redirect(url_for('member.member_home_scheduling'))

    # Query the availability with the same id
    availability = Availability.query.get(availability_id)
    if not availability:
        flash('Could not find availability', category='error')
        return redirect(url_for('member.member_home_scheduling'))

    availability.open = False

    # Bill the user
    bill = Bill(member_id=user_id, amount=50.00, date=datetime.today(), paid=True, type="Session")
    db.session.add(bill)

    # Add new session to sessions table
    new_session = Sessions(member_id=user_id, availability_id=availability_id)
    db.session.add(new_session)
    db.session.commit()

    
    flash('Session booked and billing accepted!', category='success')
    return redirect(url_for('member.member_home_scheduling'))

@member.route('/member_home/reschedule_session/<original_session_id>', methods=['POST'])
@login_required
@member_required
def reschedule_session(original_session_id):
    new_trainer_name = request.form.get('session_trainer_name')
    new_start_time = request.form.get('session_date_time')

    new_start_time = datetime.strptime(new_start_time, '%Y-%m-%dT%H:%M')

    if not new_trainer_name or not new_start_time:
        flash('Please fill out all fields', category='error')
        return redirect(url_for('member.member_home_scheduling'))

    # Get the original session
    session = Sessions.query.get(original_session_id)

    if session:
        # Get the original trainer
        original_availability = Availability.query.get(session.availability_id)
        original_trainer = Trainer.query.get(original_availability.trainer_id)

        if original_trainer.name != new_trainer_name or original_availability.available_start != new_start_time:
            new_trainer = Trainer.query.filter(Trainer.name.ilike(f'%{new_trainer_name}%')).first()

            if new_trainer:
                availability = Availability.query.filter_by(trainer_id=new_trainer.id, available_start=new_start_time, open=True).first()


                if availability:
                    # Set the original availability to open
                    original_availability.open = True

                    availability.open = False

                    # Update to match the new session booked
                    session.availability_id = availability.id

                    db.session.commit()

                    flash('Session rescheduled', category='success')
                else:
                    flash('New trainer is not available at the requested time', category='error')
            else:
                flash('Trainer not found', category='error')
        else:
            flash('New trainer name and start time are the same as the original', category='error')
    else:
        flash('Session not found', category='error')

    return redirect(url_for('member.member_home_scheduling'))

@member.route('/member_home/delete_session/<session_id>', methods=['POST'])
@login_required
@member_required
def delete_session(session_id):

    session = Sessions.query.get(session_id)
    if session:
        availability = Availability.query.get(session.availability_id)
        availability.open = True
        db.session.delete(session)
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
    class_id = request.form.get('class_id')
    credit_card_number = request.form.get('class_credit_card_number')


    # Credit card number validation
    if not credit_card_number:
        flash('Please enter a valid credit card number', category='error')
        return redirect(url_for('member.member_home_scheduling'))

    # check if class exists
    class_ = Classes.query.get(class_id)
    if not class_:
        flash('Could not find class', category='error')
        return redirect(url_for('member.member_home_scheduling'))
    

    # Check if user already booked for class
    member_class = MemberClasses.query.filter_by(member_id=user_id, class_id=class_.id).first()
    if member_class:
        flash('You are already booked for this class', category='error')
        return redirect(url_for('member.member_home_scheduling'))

    # Create new bill
    bill = Bill(member_id=user_id, amount=100.00, date=datetime.today(), paid=True, type="Class")
    db.session.add(bill)
    db.session.commit()

    # Add new member class to MemberClasses table
    new_member_class = MemberClasses(member_id=user_id, class_id=class_.id)
    db.session.add(new_member_class)
    db.session.commit()

    flash('Class booked and billing accepted!', category='success')
    return redirect(url_for('member.member_home_scheduling'))
    
