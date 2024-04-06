from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps
from .database import db
from .models import Member, Trainer, Admin, Availability, Classes, Sessions, Bill, MemberClasses,Routine, Equipment


views = Blueprint('views', __name__)


# Utiility Wrappers
def member_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not isinstance(current_user._get_current_object(), Member):
            if isinstance(current_user._get_current_object(), Trainer):
                return redirect(url_for('trainer.trainer_home'))
            elif isinstance(current_user._get_current_object(), Admin):
                return redirect(url_for('admin.admin_home'))
            else:
                return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def trainer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not isinstance(current_user._get_current_object(), Trainer):
            if isinstance(current_user._get_current_object(), Member):
                return redirect(url_for('member.member_home'))
            elif isinstance(current_user._get_current_object(), Admin):
                return redirect(url_for('admin.admin_home'))
            else:
                return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not isinstance(current_user._get_current_object(), Admin):
            if isinstance(current_user._get_current_object(), Member):
                return redirect(url_for('member.member_home'))
            elif isinstance(current_user._get_current_object(), Trainer):
                return redirect(url_for('admin.trainer_home'))
            else:
                return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def redirect_home(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if isinstance(current_user._get_current_object(), Member):
            return redirect(url_for('member.member_home'))
        elif isinstance(current_user._get_current_object(), Trainer):
            return redirect(url_for('trainer.trainer_home'))
        elif isinstance(current_user._get_current_object(), Admin):
            return redirect(url_for('admin.admin_home'))
        else:
            return f(*args, **kwargs)
    return decorated_function

# View routes
@views.route('/', methods=['GET', 'POST'])
@login_required
@redirect_home
def home():
    return redirect(url_for('auth.login'))


# Member related routes

# @views.route('/member_home/profile', methods=['GET', 'POST'])
# @login_required
# @member_required
# def member_profile():
#     current_user.is_member = True
#     return render_template('member_profile.html', user=current_user)

# @views.route('/member_home', methods=['GET', 'POST'])
# @login_required
# @member_required
# def member_home():
#     # Add trait to user that is member
#     current_user.is_member = True

#     # Get routines
#     routines = Routine.query.filter_by(member_id=current_user.id).all()

#     one_week_ago = (datetime.now() - timedelta(days=7)).date()

#     workouts_in_last_week = len([routine for routine in routines if routine.date >= one_week_ago])


#     return render_template("member_home.html", 
#                            user=current_user, 
#                            routines=routines,
#                            workouts_in_last_week=workouts_in_last_week)

# @views.route('/member_home/update_routine', methods=['POST'])
# @login_required
# @member_required
# def update_routine():
#     type = request.form.get('routine_type')
#     date = request.form.get('routine_date')

#     if not type or not date:
#         flash('While editing routine ensure fields are filled.', category='error')

#     new_routine = Routine(member_id=current_user.id, type=type, date=date)
#     db.session.add(new_routine)
#     db.session.commit()

#     flash('Routine updated', category='success')
#     return redirect(url_for('views.member_home'))

# @views.route('/member_home/add_routine', methods=['POST'])
# @login_required
# @member_required
# def add_routine():
#     type = request.form.get('new_routine_type')
#     date = request.form.get('new_routine_date')
    
#     print(type, date)
#     if not type or not date:
#         flash('Please fill out all fields', category='error')
#         return redirect(url_for('views.member_home'))


#     new_routine = Routine(member_id=current_user.id, type=type, date=date)
#     db.session.add(new_routine)
#     db.session.commit()

#     flash('Routine added', category='success')
#     return redirect(url_for('views.member_home'))

# @views.route('/member_home/delete_routine/<routine_id>', methods=['POST'])
# @login_required
# @member_required
# def delete_routine(routine_id):
#     routine = Routine.query.get(routine_id)
#     if routine:
#         db.session.delete(routine)
#         db.session.commit()

#     flash('Routine deleted', category='success')
#     return redirect(url_for('views.member_home'))

# @views.route('/member_home/scheduling', methods=['GET', 'POST'])
# @login_required
# @member_required
# def member_home_scheduling():
#     # Add trait to user that is member
#     current_user.is_member = True

#     # Traier availabilities
#     availabilities = Availability.query.all()

#     # Query based off the availability trainer_id name to get the matching trainer name from Trainers
#     for availability in availabilities:
#         trainer = Trainer.query.filter_by(id=availability.trainer_id).first()
#         availability.trainer_name = trainer.name

#     # Class schedules
#     classes = Classes.query.all()

#     # Query Sessions and filter by member_id
#     sessions = Sessions.query.filter_by(member_id=current_user.id).all()

#     # Query based off the session trainer_id name to get the matching trainer name from Trainers
#     for session in sessions:
#         trainer = Trainer.query.filter_by(id=session.trainer_id).first()
#         session.trainer_name = trainer.name

#     # Query MemberClasses for all classes that the current user is booked for
#     member_classes = MemberClasses.query.filter_by(member_id=current_user.id).all()

#     member_class_ids = [mc.class_id for mc in member_classes]

#     # Query Classes for all classes that the current user is booked for
#     booked_classes = Classes.query.filter(Classes.id.in_(member_class_ids)).all()


#     return render_template("member_home_scheduling.html", 
#                            user=current_user, 
#                            availabilities=availabilities, 
#                            classes=classes, sessions=sessions, 
#                            booked_classes=booked_classes)

# @views.route('/member_home/update_profile', methods=['POST'])
# @login_required
# @member_required
# def update_profile():
#     name = request.form.get('name')
#     profile_info = request.form.get('profile_info')
#     fitness_goals = request.form.get('fitness_goals')
#     health_metrics = request.form.get('health_metrics')
#     height = request.form.get('height')
#     weight = request.form.get('weight')
#     goal_weight = request.form.get('goal_weight')
#     goal_workouts_per_week = request.form.get('goal_workouts_per_week')

#     if (not name 
#         or not profile_info 
#         or not fitness_goals 
#         or not health_metrics 
#         or not height 
#         or not weight 
#         or not goal_weight 
#         or not goal_workouts_per_week):
#         flash('Please fill out all fields', category='error')
#         return redirect(url_for('views.member_profile'))

#     current_user.name = name
#     current_user.profile_info = profile_info
#     current_user.fitness_goals = fitness_goals
#     current_user.health_metrics = health_metrics
#     current_user.height = height
#     current_user.weight = weight
#     current_user.goal_weight = goal_weight
#     current_user.goal_workouts_per_week = goal_workouts_per_week

#     db.session.commit()

#     return redirect(url_for('views.member_profile'))


# @views.route('/member_home/book_session', methods=['POST'])
# @login_required
# @member_required
# def book_session():
#     user_id = current_user.id
#     trainer_id = request.form.get('trainer_id')

#     # remove the letter T
#     date = request.form.get('session_date').strip().replace('T', ' ')
#     date_time = date + ':00'
#     credit_card_number = request.form.get('session_credit_card_number')
#     if not credit_card_number:
#         flash('Please enter a valid credit card number', category='error')

#     # check if date_time is valid format for datetime
#     try:
#         date_time = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
#     except ValueError:
#         flash('Invalid date format', category='error')
#         return redirect(url_for('views.member_home_scheduling'))
    

#     # Remove from availabilities tuple with the same trainer id and start time
#     availability = Availability.query.filter_by(trainer_id=trainer_id, available_start=date_time).first()
#     if not availability:
#         flash('Trainer is not available at that time', category='error')
#         return redirect(url_for('views.member_home_scheduling'))
#     db.session.delete(availability)
#     db.session.commit()


#     # Create new bill
#     bill = Bill(member_id=user_id, amount=50.00, date=datetime.today(), paid=True, type="Session")
#     db.session.add(bill)
#     db.session.commit()
#     # Add new session to sessions table

#     new_session = Sessions(member_id=user_id, trainer_id=trainer_id, date_time=date_time)
#     db.session.add(new_session)
#     db.session.commit()
    
#     flash('Session booked and billing accepted!', category='success')
#     return redirect(url_for('views.member_home_scheduling'))


# @views.route('/member_home/reschedule_session/<original_session_id>', methods=['POST'])
# @login_required
# @member_required
# def reschedule_session(original_session_id):

#     new_trainer_id = request.form.get('session_trainer_id')
#     new_start_time = request.form.get('session_date_time')

#     print(new_start_time, new_trainer_id)
#     new_start_time = datetime.strptime(new_start_time, '%Y-%m-%dT%H:%M')

#     # Check if a reschedule is possible
#     availability = Availability.query.filter_by(trainer_id=new_trainer_id, available_start=new_start_time).first()

#     if availability:
#         # Get the original session
#         session = Sessions.query.get(original_session_id)

#         if session:
#             # Re-add the original session back to Availability
#             available_end = session.date_time + timedelta(hours=1)
#             original_availability = Availability(trainer_id=session.trainer_id, available_start=session.date_time, available_end=available_end)
#             db.session.add(original_availability)

#             # Update to match the new session booked
#             session.trainer_id = new_trainer_id
#             session.date_time = new_start_time

#             # Remove the availability
#             db.session.delete(availability)
            
#             db.session.commit()

#             flash('Session rescheduled', category='success')
#         else:
#             flash('Session not found', category='error')
#     else:
#         flash('Availability not found', category='error')

#     return redirect(url_for('views.member_home_scheduling'))

# @views.route('/member_home/delete_session/<session_id>', methods=['POST'])
# @login_required
# @member_required
# def delete_session(session_id):
#     new_available_start = request.form.get('new_available_start')
#     new_available_end = request.form.get('new_available_end')

#     if new_available_start and new_available_end:
#         new_available_start = datetime.strptime(new_available_start, '%Y-%m-%dT%H:%M')
#         new_available_end = datetime.strptime(new_available_end, '%Y-%m-%dT%H:%M')
#         new_availability = Availability(trainer_id=current_user.id, available_start=new_available_start, available_end=new_available_end)
#         db.session.add(new_availability)
#         db.session.commit()

#     session = Sessions.query.get(session_id)
#     session_trainer_id = request.form.get('session_trainer_id')
#     session_date_time = request.form.get('session_date_time')
#     if session:
#         db.session.delete(session)


#         # Re-add availability
#         available_start = datetime.strptime(session_date_time, '%Y-%m-%dT%H:%M')
#         available_end = available_start + timedelta(hours=1)
#         new_availability = Availability(trainer_id=session_trainer_id, available_start=available_start, available_end=available_end)
#         db.session.add(new_availability)
#         db.session.commit()
    
#     refund = Bill(member_id=current_user.id, amount=-50.00, date=datetime.today(), paid=True, type="Session")
#     db.session.add(refund)
#     db.session.commit()

#     flash('Session removed', category='success')
#     return redirect(url_for('views.member_home_scheduling'))


# @views.route('/member_home/delete_class', methods=['POST'])
# @login_required
# @member_required
# def delete_class():
#     class_id = request.form.get('class_id')
#     class_relationship = MemberClasses.query.filter_by(class_id=class_id, member_id=current_user.id).first()
#     if class_relationship:
#         db.session.delete(class_relationship)
#         db.session.commit()

#     refund = Bill(member_id=current_user.id, amount=-100.00, date=datetime.today(), paid=True, type="Class")
#     db.session.add(refund)
#     db.session.commit()

#     flash('Class booking removed', category='success')
#     return redirect(url_for('views.member_home_scheduling'))

# @views.route('/member_home/book_class', methods=['POST'])
# @login_required
# @member_required
# def book_class():
#     user_id = current_user.id
#     class_name = request.form.get('class_name')
    
#     class_time = request.form.get('class_time').strip().replace('T', ' ') + ':00'
#     credit_card_number = request.form.get('class_credit_card_number')


#     # Credit card number validation
#     if not credit_card_number:
#         flash('Please enter a valid credit card number', category='error')
#         return redirect(url_for('views.member_home_scheduling'))

#     # check if class_time is valid format for datetime
#     try:
#         class_time = datetime.strptime(class_time, '%Y-%m-%d %H:%M:%S')
#     except ValueError:
#         flash('Please ensure your entering a valid time', category='error')
#         return redirect(url_for('views.member_home_scheduling'))

#     # Query the class with the same name and time
#     class_ = Classes.query.filter(Classes.name.like(f"%{class_name}%"), Classes.schedule == class_time).first()
#     if not class_:
#         flash('Could not find class', category='error')
#         return redirect(url_for('views.member_home_scheduling'))

#     # Check if user already booked for class
#     member_class = MemberClasses.query.filter_by(member_id=user_id, class_id=class_.id).first()
#     if member_class:
#         flash('You are already booked for this class', category='error')
#         return redirect(url_for('views.member_home_scheduling'))

#     # Create new bill
#     bill = Bill(member_id=user_id, amount=50.00, date=datetime.today(), paid=True, type="Class")
#     db.session.add(bill)
#     db.session.commit()

#     # Add new member class to MemberClasses table
#     new_member_class = MemberClasses(member_id=user_id, class_id=class_.id)
#     db.session.add(new_member_class)
#     db.session.commit()

#     flash('Class booked and billing accepted!', category='success')
#     return redirect(url_for('views.member_home_scheduling'))
    

# # Trainer related routes

# @views.route('/trainer_home', methods=['GET', 'POST'])
# @login_required
# @trainer_required
# def trainer_home():
#     availabilities = Availability.query.filter_by(trainer_id=current_user.id).all()
#     for availability in availabilities:
#         trainer = Trainer.query.filter_by(id=availability.trainer_id).first()
#         availability.trainer_name = trainer.name
    
#     sessions = Sessions.query.filter_by(trainer_id=current_user.id).all()
#     for session in sessions:
#         member = Member.query.filter_by(id=session.member_id).first()
#         trainer = Trainer.query.filter_by(id=session.trainer_id).first()
#         session.member_name = member.name
#         session.trainer_name = trainer.name
    

#     members = Member.query.all()
#     return render_template("trainer_home.html", user=current_user, members=members, availabilities=availabilities, sessions=sessions)

# @views.route('/trainer_home/member_filter', methods=['GET'])
# @login_required
# @trainer_required
# def member_filter():
#     availabilities = Availability.query.filter_by(trainer_id=current_user.id).all()
#     for availability in availabilities:
#         trainer = Trainer.query.filter_by(id=availability.trainer_id).first()
#         availability.trainer_name = trainer.name

#     search = request.args.get('search')
#     members = Member.query.filter(Member.username.ilike(f'%{search}%')).all()
#     return render_template("trainer_home.html", user=current_user, members=members, availabilities=availabilities)

# @views.route('/trainer_home/update_availability', methods=['POST'])
# @login_required
# @trainer_required
# def update_availability():
#     available_starts = request.form.getlist('available_start')
#     available_ends = request.form.getlist('available_end')
#     availabilities = Availability.query.filter_by(trainer_id=current_user.id).all()

#     for i, availability in enumerate(availabilities):
#         availability.available_start = datetime.strptime(available_starts[i], '%Y-%m-%dT%H:%M')
#         availability.available_end = datetime.strptime(available_ends[i], '%Y-%m-%dT%H:%M')

#     db.session.commit()

#     flash('Availability updated', category='success')
#     return redirect(url_for('views.trainer_home'))

# @views.route('/trainer_home/delete_availability/<availability_id>', methods=['POST'])
# @login_required
# @trainer_required
# def delete_availability(availability_id):
#     availability = Availability.query.get(availability_id)
#     if availability:
#         db.session.delete(availability)
#         db.session.commit()

#     flash('Availability deleted', category='success')
#     return redirect(url_for('views.trainer_home'))

# @views.route('/trainer_home/add_availability', methods=['POST'])
# @login_required
# @trainer_required
# def add_availability():
#     new_available_start = request.form.get('new_available_start')
#     new_available_end = request.form.get('new_available_end')

#     if new_available_start and new_available_end:
#         new_available_start = datetime.strptime(new_available_start, '%Y-%m-%dT%H:%M')
#         new_available_end = datetime.strptime(new_available_end, '%Y-%m-%dT%H:%M')
#         new_availability = Availability(trainer_id=current_user.id, available_start=new_available_start, available_end=new_available_end)
#         db.session.add(new_availability)
#         db.session.commit()

#     flash('Availability added', category='success')
#     return redirect(url_for('views.trainer_home'))


# @views.route('/trainer_home/delete_session/<session_id>', methods=['POST'])
# @login_required
# @trainer_required
# def trainer_delete_session(session_id):
#     session = Sessions.query.get(session_id)
#     if session:
#         db.session.delete(session)
#         db.session.commit()

#     refund = Bill(member_id=session.member_id, amount=-50.00, date=datetime.today(), paid=True, type="Session")
#     db.session.add(refund)
#     db.session.commit()

#     flash('Session deleted', category='success')
#     return redirect(url_for('views.trainer_home'))


# # Admin related routes

# @views.route('/admin_home', methods=['GET', 'POST'])
# @login_required
# @admin_required
# def admin_home():
#     # get all maintenances to view
#     all_equipment = Equipment.query.all()
    
#     # get all classes to view
#     classes = Classes.query.all()

#     # get all trainers to view
#     trainers = Trainer.query.all()


#     for class_ in classes:
#         trainer = Trainer.query.filter_by(id=class_.trainer_id).first()
#         class_.trainer_name = trainer.name

#     # Get all Bills
#     bills = Bill.query.all()

#     # Attach customer names via member_id
#     for bill in bills:
#         member = Member.query.filter_by(id=bill.member_id).first()
#         bill.member_name = member.name
    

#     return render_template("admin_home.html", 
#                            user=current_user,
#                             all_equipment=all_equipment,
#                             classes=classes,
#                             trainers=trainers,
#                             bills=bills)


# @views.route('/admin_home/update_maintenace', methods=['POST'])
# @login_required
# @admin_required
# def update_maintenance():
    
#     equipment_id = request.form.get('equipment_id')
#     equipment_type = request.form.get('equipment_type')
#     last_maintained = request.form.get('last_maintained')
#     next_maintenance = request.form.get('next_maintenance')

#     if not equipment_type or not last_maintained or not next_maintenance:
#         print(equipment_type, last_maintained, next_maintenance)
#         flash('Please fill out all fields when editing equipment', category='error')
#         return redirect(url_for('views.admin_home'))

#     equipment = Equipment.query.get(equipment_id)
#     if equipment:
#         equipment.type = equipment_type
#         equipment.last_maintained = last_maintained
#         equipment.next_maintenance = next_maintenance
#         db.session.commit()

#     flash('Maintenance schedule updated', category='success')
#     return redirect(url_for('views.admin_home'))

# @views.route('/admin_home/maintain_equipment/<equipment_id>', methods=['POST'])
# @login_required
# @admin_required
# def maintain_equipment(equipment_id):
#     equipment = Equipment.query.get(equipment_id)
#     if equipment:
#         equipment.last_maintained = datetime.now().strftime('%Y-%m-%d %H:%M')
#         db.session.commit()

#     flash('Equipment maintained', category='success')
#     return redirect(url_for('views.admin_home'))

# @views.route('/admin_home/delete_equipment/<equipment_id>', methods=['POST'])
# @login_required
# @admin_required
# def delete_equipment(equipment_id):
#     equipment = Equipment.query.get(equipment_id)
#     if equipment:
#         db.session.delete(equipment)
#         db.session.commit()

#     flash('Equipment deleted', category='success')
#     return redirect(url_for('views.admin_home'))

# @views.route('/admin_home/add_equipment', methods=['POST'])
# @login_required
# @admin_required
# def add_equipment():
#     equipment_type = request.form.get('new_type')
#     last_maintained = datetime.now().strftime('%Y-%m-%d %H:%M')
#     next_maintenance = request.form.get('new_next_maintenance').strip().replace('T', ' ') + ':00'

#     if not equipment_type or not next_maintenance:
#         flash('Please fill out all fields', category='error')
#         return redirect(url_for('views.admin_home'))

#     new_equipment = Equipment(type=equipment_type, last_maintained=last_maintained, next_maintenance=next_maintenance)
#     db.session.add(new_equipment)
#     db.session.commit()

#     flash('Equipment added', category='success')
#     return redirect(url_for('views.admin_home'))


# @views.route('/admin_home/update_class_schedule', methods=['POST'])
# @login_required
# @admin_required
# def update_class_schedule():
#     class_id = request.form.get('class_id')
#     trainer_id = request.form.get('trainer_id')

#     class_name = request.form.get('class_name')
#     class_room = request.form.get('class_room')
#     schedule_from_form = request.form.get('class_schedule')

#     if not trainer_id or not class_name or not class_room or not schedule_from_form:
#         flash('Please fill out all fields', category='error')
#         return redirect(url_for('views.admin_home'))

#     # Parse schedule after verifying one was entered
#     schedule = datetime.strptime(schedule_from_form.strip().replace('T', ' ') + ':00', '%Y-%m-%d %H:%M:%S')

#     # Query Sessions to check if trainer is available
#     sessions = Sessions.query.filter_by(trainer_id=trainer_id).all()
#     for session in sessions:
#         print(session.date_time, schedule)
#         if session.date_time == schedule:
#             flash('Trainer is not available at that time, has a conflicting session', category='error')
#             return redirect(url_for('views.admin_home'))
        
#     # Query Classes to see if room and trainer are available
#     classes = Classes.query.all()
#     for class_ in classes:
#         if class_.schedule == schedule and class_.room == class_room:
#             flash('Room is not available at that time', category='error')
#             return redirect(url_for('views.admin_home'))
#         if class_.schedule == schedule and class_.trainer_id == int(trainer_id):
#             flash('Trainer is not available at that time, responsible for another class at this time', category='error')
#             return redirect(url_for('views.admin_home'))

#     class_ = Classes.query.get(class_id)
#     if class_:
#         class_.trainer_id = trainer_id
#         class_.name = class_name
#         class_.room = class_room
#         class_.schedule = schedule
#         db.session.commit()

#     flash('Class schedule updated', category='success')
#     return redirect(url_for('views.admin_home'))


# @views.route('/admin_home/delete_class_schedule/<class_schedule_id>', methods=['POST'])
# @login_required
# @admin_required
# def delete_class_schedule(class_schedule_id):
#     class_ = Classes.query.get(class_schedule_id)
#     if class_:
#         db.session.delete(class_)
#         db.session.commit()

#     # Issue refunds to all memebers who booked the class
#     member_classes = MemberClasses.query.filter_by(class_id=class_schedule_id).all()
#     for member_class in member_classes:
#         refund = Bill(member_id=member_class.member_id, amount=-100.00, date=datetime.today(), paid=True, type="Class")
#         db.session.add(refund)
#         db.session.commit()

#     flash('Class schedule deleted', category='success')
#     return redirect(url_for('views.admin_home'))

# @views.route('/admin_home/add_class_schedule', methods=['POST'])
# @login_required
# @admin_required
# def add_class_schedule():
#     class_name = request.form.get('new_class_name')
#     room = request.form.get('new_room')
#     schedule_from_form = request.form.get('new_schedule')
#     trainer_id = request.form.get('new_trainer_id')

#     if not class_name or not room or not schedule_from_form:
#         flash('Please fill out all fields', category='error')
#         return redirect(url_for('views.admin_home'))
    
#     # Parse schedule after verifying one was entered
#     schedule = datetime.strptime(schedule_from_form.strip().replace('T', ' ') + ':00', '%Y-%m-%d %H:%M:%S')
    
#     # Query Sessions to check if trainer is available
#     sessions = Sessions.query.filter_by(trainer_id=trainer_id).all()
#     for session in sessions:
#         print(session.date_time, schedule)
#         if session.date_time == schedule:
#             flash('Trainer is not available at that time, has a conflicting session', category='error')
#             return redirect(url_for('views.admin_home'))
        
#     # Query Classes to see if room and trainer are available
#     classes = Classes.query.all()
#     for class_ in classes:
#         if class_.schedule == schedule and class_.room == room:
#             flash('Room is not available at that time', category='error')
#             return redirect(url_for('views.admin_home'))
#         if class_.schedule == schedule and class_.trainer_id == int(trainer_id):
#             flash('Trainer is not available at that time, responsible for another class at this time', category='error')
#             return redirect(url_for('views.admin_home'))

#     print(trainer_id, class_name, room, schedule)
#     new_class = Classes(trainer_id=trainer_id, name=class_name, room=room, schedule=schedule)
#     db.session.add(new_class)
#     db.session.commit()

#     flash('Class schedule added', category='success')
#     return redirect(url_for('views.admin_home'))

# @views.route('/admin_home/pay_bill/<bill_id>', methods=['POST'])
# @login_required
# @admin_required
# def pay_bill(bill_id):
#     bill = Bill.query.get(bill_id)
#     if bill:
#         bill.paid = True
#         db.session.commit()

#     flash('Bill processed', category='success')
#     return redirect(url_for('views.admin_home'))

# @views.route('/admin_home/add_bill', methods=['POST'])
# @login_required
# @admin_required
# def add_bill():
#     member_id = request.form.get('new_member_id')
#     member_name = request.form.get('new_member_name')
#     amount = request.form.get('new_amount')
#     type = request.form.get('new_type')
#     date = request.form.get('new_date')
#     paid = True if request.form.get('new_paid') == 'True' else False

#     if not member_id or not member_name or not amount or not type or not date:
#         flash('Please fill out all fields', category='error')
#         return redirect(url_for('views.admin_home'))

#     # Check if member id and name are valid
#     member = Member.query.filter_by(id=member_id, name=member_name).first()
#     if not member:
#         flash('Member could not found with that ID and name', category='error')
#         return redirect(url_for('views.admin_home'))
    

#     new_bill = Bill(member_id=member_id, amount=amount, date=date, paid=paid, type=type)
#     db.session.add(new_bill)
#     db.session.commit()

#     flash('Bill added', category='success')
#     return redirect(url_for('views.admin_home'))