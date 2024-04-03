import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps
from .database import db
from .models import Member, Trainer, Admin, Availability, Classes, Sessions, Bill

views = Blueprint('views', __name__)


# Utiility Wrappers
def member_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not isinstance(current_user._get_current_object(), Member):
            if isinstance(current_user._get_current_object(), Trainer):
                return redirect(url_for('views.trainer_home'))
            elif isinstance(current_user._get_current_object(), Admin):
                return redirect(url_for('views.admin_home'))
            else:
                return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def trainer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not isinstance(current_user._get_current_object(), Trainer):
            if isinstance(current_user._get_current_object(), Member):
                return redirect(url_for('views.member_home'))
            elif isinstance(current_user._get_current_object(), Admin):
                return redirect(url_for('views.admin_home'))
            else:
                return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not isinstance(current_user._get_current_object(), Admin):
            if isinstance(current_user._get_current_object(), Member):
                return redirect(url_for('views.member_home'))
            elif isinstance(current_user._get_current_object(), Trainer):
                return redirect(url_for('views.trainer_home'))
            else:
                return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def redirect_home(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if isinstance(current_user._get_current_object(), Member):
            return redirect(url_for('views.member_home'))
        elif isinstance(current_user._get_current_object(), Trainer):
            return redirect(url_for('views.trainer_home'))
        elif isinstance(current_user._get_current_object(), Admin):
            return redirect(url_for('views.admin_home'))
        else:
            return f(*args, **kwargs)
    return decorated_function

# View routes
@views.route('/', methods=['GET', 'POST'])
@login_required
@redirect_home
def home():
    return redirect(url_for('auth.login'))

@views.route('/member_home', methods=['GET', 'POST'])
@login_required
@member_required
def member_home():
    # Traier availabilities
    availabilities = Availability.query.all()

    # Class schedules
    classes = Classes.query.all()

    return render_template("member_home.html", user=current_user, availabilities=availabilities, classes=classes)

@views.route('/member_home/update_profile', methods=['POST'])
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
    print(name, profile_info, fitness_goals, health_metrics, height, weight, goal_weight, goal_workouts_per_week)

    current_user.name = name
    current_user.profile_info = profile_info
    current_user.fitness_goals = fitness_goals
    current_user.health_metrics = health_metrics
    current_user.height = height
    current_user.weight = weight
    current_user.goal_weight = goal_weight
    current_user.goal_workouts_per_week = goal_workouts_per_week

    db.session.commit()

    return redirect(url_for('views.member_home'))


@views.route('/member_home/book_session', methods=['POST'])
@login_required
@member_required
def book_session():
    user_id = current_user.id
    trainer_id = request.form.get('trainer_id')

    from datetime import datetime

    # remove the letter T
    date = request.form.get('date').strip().replace('T', ' ')
    date_time = date + ':00'
    credit_card_number = request.form.get('credit_card_number')
    if not credit_card_number:
        flash('Please enter a valid credit card number', category='error')

    # check if date_time is valid format for datetime
    try:
        date_time = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        flash('Invalid date format', category='error')
        return redirect(url_for('views.member_home'))
    

    # Remove from availabilities tuple with the same trainer id and start time
    availability = Availability.query.filter_by(trainer_id=trainer_id, available_start=date_time).first()
    if not availability:
        flash('Trainer is not available at that time', category='error')
        return redirect(url_for('views.member_home'))
    db.session.delete(availability)
    db.session.commit()


    # Create new bill
    bill = Bill(member_id=user_id, amount=50.00, date=datetime.today(),)
    db.session.add(bill)
    db.session.commit()
    # Add new session to sessions table

    new_session = Sessions(member_id=user_id, trainer_id=trainer_id, date_time=date_time)
    db.session.add(new_session)
    db.session.commit()
    
    flash('Session booked and billing accepted!', category='success')
    return redirect(url_for('views.member_home'))
    

@views.route('/trainer_home', methods=['GET', 'POST'])
@login_required
@trainer_required
def trainer_home():

    members = Member.query.all()
    return render_template("trainer_home.html", user=current_user, members=members)

@views.route('/trainer_home/member_filter', methods=['GET'])
@login_required
@trainer_required
def member_filter():
    search = request.args.get('search')
    members = Member.query.filter(Member.username.ilike(f'%{search}%')).all()
    return render_template("trainer_home.html", user=current_user, members=members)

@views.route('/admin_home', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_home():
    return render_template("admin_home.html", user=current_user)