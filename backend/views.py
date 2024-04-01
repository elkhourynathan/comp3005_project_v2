from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps
from .database import db
from .models import Member, Trainer, Admin

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
    return render_template("member_home.html", user=current_user)


@views.route('/trainer_home', methods=['GET', 'POST'])
@login_required
@trainer_required
def trainer_home():
    return render_template("trainer_home.html", user=current_user)

@views.route('/admin_home', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_home():
    return render_template("admin_home.html", user=current_user)