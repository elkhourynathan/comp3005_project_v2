from flask import Blueprint, redirect, render_template, request, flash, redirect, url_for
from .models import Member, Trainer, Admin, Bill
from datetime import datetime
from .database import db
from flask_login import login_user, logout_user, login_required, current_user

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = Member.query.filter_by(username=username).first()
        if not user:
            user = Trainer.query.filter_by(username=username).first()
        if not user:
            user = Admin.query.filter_by(username=username).first()

        if user:
            if user.password == password:
                flash('Logged in successfully!', category='success')
                login_user(user, remember=False)
                if isinstance(user, Member):
                    return redirect(url_for('member.member_home'))
                elif isinstance(user, Trainer):
                    return redirect(url_for('trainer.trainer_home'))
                else:  # user is an Admin
                    return redirect(url_for('admin.admin_home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Username does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/signup', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')

        user = Member.query.filter_by(username=username).first()
        if user:
            flash('Username already exists.', category='error')
        else:
            new_user = Member(username=username, password=password, name=name, profile_info='', fitness_goals='', health_metrics='', height=0, weight=0, goal_weight=0, goal_workouts_per_week=0)
            db.session.add(new_user)
            db.session.commit()
            new_user_id = Member.query.filter_by(username=username).first().id
            membership_bill = Bill(amount=100, member_id=new_user_id, type='Membership', paid=False, date=datetime.today())
            db.session.add(membership_bill)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("signup.html", user=current_user)
