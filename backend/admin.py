from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .database import db
from .models import Member, Trainer, Availability, Classes, Bill, MemberClasses, Equipment, Room
from .views import admin_required

admin = Blueprint('admin', __name__)


# Admin related routes

@admin.route('/admin_home', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_home():
    all_equipment = Equipment.query.all()
    members = Member.query.all()
    trainers = Trainer.query.all()
    rooms = Room.query.all()
    bills = db.session.query(
        Bill.id.label("id"),
        Bill.member_id.label("member_id"),
        Bill.amount.label("amount"),
        Bill.date.label("date"),
        Bill.paid.label("paid"),
        Bill.type.label("type"),
        Member.name.label("member_name")
    ).join(Member, Bill.member_id == Member.id).all()

    classes = db.session.query(
        Classes.id.label("id"),
        Classes.name.label("name"),
        Room.name.label("room"),
        Trainer.id.label("trainer_id"),
        Trainer.name.label("trainer_name"),
        Availability.available_start.label("schedule")
    ).join(Availability, Classes.availability_id == Availability.id) \
     .join(Room, Classes.room_id == Room.id) \
     .join(Trainer, Availability.trainer_id == Trainer.id).all()

    # Sort all lists by id
    all_equipment.sort(key=lambda x: x.id)
    classes.sort(key=lambda x: x.id)
    trainers.sort(key=lambda x: x.id)
    bills.sort(key=lambda x: x.id)
    rooms.sort(key=lambda x: x.id)

    return render_template("admin_home.html", 
                           user=current_user,
                            all_equipment=all_equipment,
                            classes=classes,
                            trainers=trainers,
                            rooms=rooms,
                            bills=bills,
                            members=members)


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
    next_maintenance = request.form.get('new_next_maintenance')
    next_maintenance = datetime.strptime(next_maintenance, '%Y-%m-%dT%H:%M')

    if not equipment_type or not next_maintenance:
        flash('Please fill out all fields', category='error')
        return redirect(url_for('admin.admin_home'))

    new_equipment = Equipment(type=equipment_type, last_maintained=last_maintained, next_maintenance=next_maintenance)
    db.session.add(new_equipment)
    db.session.commit()

    flash('Equipment added', category='success')
    return redirect(url_for('admin.admin_home'))


@admin.route('/admin_home/update_class_schedule/<class_schedule_id>', methods=['POST'])
@login_required
@admin_required
def update_class_schedule(class_schedule_id):
    class_id = class_schedule_id
    trainer_id = int(request.form.get('trainer_id'))
    class_name = request.form.get('class_name')
    room_id = int(request.form.get('room_id'))
    schedule_from_form = request.form.get('class_schedule')

    if not trainer_id or not class_name or not room_id or not schedule_from_form:
        flash('Please fill out all fields', category='error')
        return redirect(url_for('admin.admin_home'))
    
    schedule = datetime.strptime(schedule_from_form.strip().replace('T', ' ') + ':00', '%Y-%m-%d %H:%M:%S')

    # Check if anything was changed
    class_ = Classes.query.get(class_id)
    original_availability = Availability.query.get(class_.availability_id)
    original_trainer = Trainer.query.get(original_availability.trainer_id)


    # print all the values and the truthy values
    if (original_trainer.id == trainer_id
        and class_.name == class_name 
        and class_.room_id == room_id 
        and original_availability.available_start == schedule):
        flash('No changes were made', category='error')
        return redirect(url_for('admin.admin_home'))

    # Check room availability
    other_classes = Classes.query.join(Availability).filter(
        Classes.room_id == room_id,
        Availability.available_start == schedule,
        Classes.id != class_.id  # Exclude the current class from the check
    ).first()
    if other_classes:
        flash('Room is already booked for another class at the given time.', category='error')
        return redirect(url_for('admin.admin_home'))

    # Check trainer time collisions
    collision = Availability.query.filter(
        Availability.trainer_id == trainer_id,
        Availability.available_start <= schedule,
        Availability.available_end >= schedule,
        Availability.id != class_.availability_id,
        Availability.open == False
    ).first()

    if collision:
        flash('Trainer has a colliding availability.', category='error')
        return redirect(url_for('admin.admin_home'))        

    # If no collision, proceed to update or create availability
    if original_availability.trainer_id != trainer_id or original_availability.available_start != schedule:
        # Open the previous availability if it's not being used for another class
        original_availability.open = True

        # Check if trainer has a open availability at this time
        open_availability = Availability.query.filter(
            Availability.trainer_id == trainer_id,
            Availability.available_start == schedule,
            Availability.open == True
        ).first()
        if open_availability:
            open_availability.open = False
            class_.availability_id = open_availability.id
        else:
            # Create a new availability
            new_availability = Availability(trainer_id=trainer_id, available_start=schedule, available_end=schedule + timedelta(hours=1), open=False)
            db.session.add(new_availability)
            db.session.flush() 

            # Assign the new availability to the class
            class_.availability_id = new_availability.id
    
    # Update class details
    class_.name = class_name
    class_.room_id = room_id

    db.session.commit()
    flash('Class schedule updated successfully.', category='success')
    return redirect(url_for('admin.admin_home'))


@admin.route('/admin_home/delete_class_schedule/<class_schedule_id>', methods=['POST'])
@login_required
@admin_required
def delete_class_schedule(class_schedule_id):
    class_ = Classes.query.get(class_schedule_id)
    if class_:
        availability = Availability.query.get(class_.availability_id)
        db.session.delete(availability)
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
    trainer_id = int(request.form.get('new_trainer_id'))
    class_name = request.form.get('new_class_name')
    room_id = int(request.form.get('new_room'))
    schedule_from_form = request.form.get('new_schedule')

    if not trainer_id or not class_name or not room_id or not schedule_from_form:
        flash('Please fill out all fields.', category='error')
        return redirect(url_for('admin.admin_home'))
    
    # Convert the schedule from form input to a datetime object
    schedule = datetime.strptime(schedule_from_form.strip().replace('T', ' ') + ':00', '%Y-%m-%d %H:%M:%S')

    # Check for trainer availability
    collision = Availability.query.filter(
        Availability.trainer_id == trainer_id,
        Availability.available_start <= schedule,
        Availability.available_end >= schedule,
    ).first()
    
    if collision:
        flash('Trainer has a colliding availability.', category='error')
        return redirect(url_for('admin.admin_home'))

    # Check for room availability
    room_collision = Classes.query.join(Availability, Classes.availability_id == Availability.id).filter(
        Classes.room_id == room_id,
        Availability.available_start == schedule,
    ).first()
    
    if room_collision:
        flash('The selected room is already booked at the specified time.', category='error')
        return redirect(url_for('admin.admin_home'))
    
    # If no collision, create a new availability
    new_availability = Availability(
        trainer_id=trainer_id, 
        available_start=schedule, 
        available_end=schedule + timedelta(hours=1), 
        open=False  
    )
    db.session.add(new_availability)
    db.session.flush()  

    # Create a new class with the new availability
    new_class = Classes(
        name=class_name, 
        room_id=room_id, 
        availability_id=new_availability.id
    )
    db.session.add(new_class)
    db.session.commit()

    flash('New class schedule added successfully.', category='success')
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
    member_name = Member.query.get(member_id).name
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


@admin.route('/add_room', methods=['POST'])
@login_required
@admin_required
def add_room():
    new_room_name = request.form.get('new_room_name')
    if not new_room_name:
        flash('Room name cannot be empty.', 'error')
        return redirect(url_for('admin.admin_home'))

    new_room = Room(name=new_room_name)
    db.session.add(new_room)
    db.session.commit()
    flash('Room added successfully.', 'success')
    return redirect(url_for('admin.admin_home'))

@admin.route('/update_room/<room_id>', methods=['POST'])
@login_required
@admin_required
def update_room(room_id):
    room = Room.query.get(room_id)
    room_name = request.form.get(f'room_name_{room_id}')
    
    if not room_name:
        flash('Room name cannot be empty.', 'error')
        return redirect(url_for('admin.admin_home'))

    room.name = room_name
    db.session.commit()
    flash('Room updated successfully.', 'success')
    return redirect(url_for('admin.admin_home'))

@admin.route('/delete_room/<room_id>', methods=['POST'])
@login_required
@admin_required
def delete_room(room_id):
    room = Room.query.get(room_id)

    classes = Classes.query.filter_by(room_id=room_id).all()
    for class_ in classes:
        delete_class_schedule(class_.id)
    

    db.session.delete(room)
    db.session.commit()
    flash('Room deleted successfully.', 'success')
    return redirect(url_for('admin.admin_home'))