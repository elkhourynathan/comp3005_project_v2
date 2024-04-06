from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps
from .database import db
from .models import Member, Trainer, Admin, Availability, Classes, Sessions, Bill, MemberClasses,Routine, Equipment
from .views import admin_required

admin = Blueprint('admin', __name__)


# Admin related routes

@admin.route('/admin_home', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_home():
    # get all maintenances to view
    all_equipment = Equipment.query.all()
    
    # get all classes to view
    classes = Classes.query.all()

    # get all trainers to view
    trainers = Trainer.query.all()


    for class_ in classes:
        trainer = Trainer.query.filter_by(id=class_.trainer_id).first()
        class_.trainer_name = trainer.name

    # Get all Bills
    bills = Bill.query.all()

    # Attach customer names via member_id
    for bill in bills:
        member = Member.query.filter_by(id=bill.member_id).first()
        bill.member_name = member.name
    
    # Sort all lists by id
    all_equipment.sort(key=lambda x: x.id)
    classes.sort(key=lambda x: x.id)
    trainers.sort(key=lambda x: x.id)
    bills.sort(key=lambda x: x.id)

    return render_template("admin_home.html", 
                           user=current_user,
                            all_equipment=all_equipment,
                            classes=classes,
                            trainers=trainers,
                            bills=bills)


@admin.route('/admin_home/update_maintenace', methods=['POST'])
@login_required
@admin_required
def update_maintenance():
    
    equipment_id = request.form.get('equipment_id')
    equipment_type = request.form.get('equipment_type')
    last_maintained = request.form.get('last_maintained')
    next_maintenance = request.form.get('next_maintenance')

    if not equipment_type or not last_maintained or not next_maintenance:
        print(equipment_type, last_maintained, next_maintenance)
        flash('Please fill out all fields when editing equipment', category='error')
        return redirect(url_for('admin.admin_home'))

    equipment = Equipment.query.get(equipment_id)
    if equipment:
        equipment.type = equipment_type
        equipment.last_maintained = last_maintained
        equipment.next_maintenance = next_maintenance
        db.session.commit()

    flash('Maintenance schedule updated', category='success')
    return redirect(url_for('admin.admin_home'))

@admin.route('/admin_home/maintain_equipment/<equipment_id>', methods=['POST'])
@login_required
@admin_required
def maintain_equipment(equipment_id):
    equipment = Equipment.query.get(equipment_id)
    if equipment:
        equipment.last_maintained = datetime.now().strftime('%Y-%m-%d %H:%M')
        db.session.commit()

    flash('Equipment maintained', category='success')
    return redirect(url_for('admin.admin_home'))

@admin.route('/admin_home/delete_equipment/<equipment_id>', methods=['POST'])
@login_required
@admin_required
def delete_equipment(equipment_id):
    equipment = Equipment.query.get(equipment_id)
    if equipment:
        db.session.delete(equipment)
        db.session.commit()

    flash('Equipment deleted', category='success')
    return redirect(url_for('admin.admin_home'))

@admin.route('/admin_home/add_equipment', methods=['POST'])
@login_required
@admin_required
def add_equipment():
    equipment_type = request.form.get('new_type')
    last_maintained = datetime.now().strftime('%Y-%m-%d %H:%M')
    next_maintenance = request.form.get('new_next_maintenance').strip().replace('T', ' ') + ':00'

    if not equipment_type or not next_maintenance:
        flash('Please fill out all fields', category='error')
        return redirect(url_for('admin.admin_home'))

    new_equipment = Equipment(type=equipment_type, last_maintained=last_maintained, next_maintenance=next_maintenance)
    db.session.add(new_equipment)
    db.session.commit()

    flash('Equipment added', category='success')
    return redirect(url_for('admin.admin_home'))


@admin.route('/admin_home/update_class_schedule', methods=['POST'])
@login_required
@admin_required
def update_class_schedule():
    class_id = request.form.get('class_id')
    trainer_id = request.form.get('trainer_id')

    class_name = request.form.get('class_name')
    class_room = request.form.get('class_room')
    schedule_from_form = request.form.get('class_schedule')

    if not trainer_id or not class_name or not class_room or not schedule_from_form:
        flash('Please fill out all fields', category='error')
        return redirect(url_for('admin.admin_home'))

    # Parse schedule after verifying one was entered
    schedule = datetime.strptime(schedule_from_form.strip().replace('T', ' ') + ':00', '%Y-%m-%d %H:%M:%S')

    # Query Sessions to check if trainer is available
    sessions = Sessions.query.filter_by(trainer_id=trainer_id).all()
    for session in sessions:
        print(session.date_time, schedule)
        if session.date_time == schedule:
            flash('Trainer is not available at that time, has a conflicting session', category='error')
            return redirect(url_for('admin.admin_home'))
        
    # Query Classes to see if room and trainer are available
    classes = Classes.query.all()
    for class_ in classes:
        if class_.schedule == schedule and class_.room == class_room:
            flash('Room is not available at that time', category='error')
            return redirect(url_for('admin.admin_home'))
        if class_.schedule == schedule and class_.trainer_id == int(trainer_id):
            flash('Trainer is not available at that time, responsible for another class at this time', category='error')
            return redirect(url_for('admin.admin_home'))

    class_ = Classes.query.get(class_id)
    if class_:
        class_.trainer_id = trainer_id
        class_.name = class_name
        class_.room = class_room
        class_.schedule = schedule
        db.session.commit()

    flash('Class schedule updated', category='success')
    return redirect(url_for('admin.admin_home'))


@admin.route('/admin_home/delete_class_schedule/<class_schedule_id>', methods=['POST'])
@login_required
@admin_required
def delete_class_schedule(class_schedule_id):
    class_ = Classes.query.get(class_schedule_id)
    if class_:
        db.session.delete(class_)
        db.session.commit()

    # Issue refunds to all memebers who booked the class
    member_classes = MemberClasses.query.filter_by(class_id=class_schedule_id).all()
    for member_class in member_classes:
        refund = Bill(member_id=member_class.member_id, amount=-100.00, date=datetime.today(), paid=True, type="Class")
        db.session.add(refund)
        db.session.commit()

    flash('Class schedule deleted', category='success')
    return redirect(url_for('admin.admin_home'))

@admin.route('/admin_home/add_class_schedule', methods=['POST'])
@login_required
@admin_required
def add_class_schedule():
    class_name = request.form.get('new_class_name')
    room = request.form.get('new_room')
    schedule_from_form = request.form.get('new_schedule')
    trainer_id = request.form.get('new_trainer_id')

    if not class_name or not room or not schedule_from_form:
        flash('Please fill out all fields', category='error')
        return redirect(url_for('admin.admin_home'))
    
    # Parse schedule after verifying one was entered
    schedule = datetime.strptime(schedule_from_form.strip().replace('T', ' ') + ':00', '%Y-%m-%d %H:%M:%S')
    
    # Query Sessions to check if trainer is available
    sessions = Sessions.query.filter_by(trainer_id=trainer_id).all()
    for session in sessions:
        print(session.date_time, schedule)
        if session.date_time == schedule:
            flash('Trainer is not available at that time, has a conflicting session', category='error')
            return redirect(url_for('admin.admin_home'))
        
    # Query Classes to see if room and trainer are available
    classes = Classes.query.all()
    for class_ in classes:
        if class_.schedule == schedule and class_.room == room:
            flash('Room is not available at that time', category='error')
            return redirect(url_for('admin.admin_home'))
        if class_.schedule == schedule and class_.trainer_id == int(trainer_id):
            flash('Trainer is not available at that time, responsible for another class at this time', category='error')
            return redirect(url_for('admin.admin_home'))

    print(trainer_id, class_name, room, schedule)
    new_class = Classes(trainer_id=trainer_id, name=class_name, room=room, schedule=schedule)
    db.session.add(new_class)
    db.session.commit()

    flash('Class schedule added', category='success')
    return redirect(url_for('admin.admin_home'))

@admin.route('/admin_home/pay_bill/<bill_id>', methods=['POST'])
@login_required
@admin_required
def pay_bill(bill_id):
    bill = Bill.query.get(bill_id)
    if bill:
        bill.paid = True
        db.session.commit()

    flash('Bill processed', category='success')
    return redirect(url_for('admin.admin_home'))

@admin.route('/admin_home/add_bill', methods=['POST'])
@login_required
@admin_required
def add_bill():
    member_id = request.form.get('new_member_id')
    member_name = request.form.get('new_member_name')
    amount = request.form.get('new_amount')
    type = request.form.get('new_type')
    date = request.form.get('new_date')
    paid = True if request.form.get('new_paid') == 'True' else False

    if not member_id or not member_name or not amount or not type or not date:
        flash('Please fill out all fields', category='error')
        return redirect(url_for('admin.admin_home'))

    # Check if member id and name are valid
    member = Member.query.filter_by(id=member_id, name=member_name).first()
    if not member:
        flash('Member could not found with that ID and name', category='error')
        return redirect(url_for('admin.admin_home'))
    

    new_bill = Bill(member_id=member_id, amount=amount, date=date, paid=paid, type=type)
    db.session.add(new_bill)
    db.session.commit()

    flash('Bill added', category='success')
    return redirect(url_for('admin.admin_home'))