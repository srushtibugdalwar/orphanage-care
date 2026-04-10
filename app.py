from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

import os
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'medicine.db')
app.config['SECRET_KEY'] = 'secret'

db = SQLAlchemy(app)
scheduler = BackgroundScheduler() 
scheduler.start()


def send_reminder(child_id, medicine):
    with app.app_context():
        child = Child.query.get(child_id)
        child_name = child.name if child else f"ID {child_id}"
        print("REMINDER TRIGGERED")
        print(f"Give {medicine} to {child_name} (ID: {child_id})")

# ---------------- MODELS ----------------

class Caretaker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(100))


class Child(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))   


class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'))
    name = db.Column(db.String(100))
    dosage = db.Column(db.String(50))
    time = db.Column(db.String(50))



class HealthRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer)
    diagnose = db.Column(db.String(200))
    medicine = db.Column(db.String(100))
    dosage = db.Column(db.String(50))
    datetime = db.Column(db.DateTime) 
    is_done = db.Column(db.Boolean, default=False) 
# ---------------- ROUTES ----------------

# LANDING PAGE
@app.route("/")
def index():
    return render_template("landing.html")

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        pwd = request.form["password"]

        caretaker = Caretaker.query.filter_by(email=email, password=pwd).first()

        if caretaker:
            session["user"] = caretaker.username
            return redirect("/dashboard")

        else:
            return "Invalid credentials"

    return render_template("login.html")

# DASHBOARD



@app.route('/dashboard')
def dashboard():
    children = Child.query.all()

    now = datetime.now()

    due_records = HealthRecord.query.filter(
        HealthRecord.datetime <= now,
        HealthRecord.is_done == False
    ).all()

    child_map = {str(child.id): child.name for child in children}
    due_child_ids = [record.child_id for record in due_records]

    return render_template(
        'dashboard.html',
        children=children,
        due_records=due_records,
        child_map=child_map,
        due_child_ids=due_child_ids
    )
# ADD CHILD
@app.route('/add_child', methods=['POST'])
def add_child():
    name = request.form['name']
    age = request.form['age']
    gender = request.form['gender']
    custom_id = request.form.get('child_id')

    if custom_id:
        try:
            custom_id = int(custom_id)
            existing = Child.query.get(custom_id)
            if existing:
                flash(f"Error: Child ID {custom_id} is already taken!", "danger")
                return redirect('/dashboard')
        except ValueError:
            flash("Error: Invalid Child ID format!", "danger")
            return redirect('/dashboard')
    else:
        custom_id = None

    new_child = Child(id=custom_id, name=name, age=age, gender=gender)
    db.session.add(new_child)
    db.session.commit()

    flash(f"Child {name} registered successfully (ID: {new_child.id})", "success")
    return redirect('/dashboard')

# ADD MEDICINE
@app.route("/add_medicine", methods=["POST"])
def add_medicine():
    child_id = request.form["child_id"]
    name = request.form["name"]
    dosage = request.form["dosage"]
    time = request.form["time"]

    med = Medicine(child_id=child_id, name=name, dosage=dosage, time=time)
    db.session.add(med)
    db.session.commit()

    return redirect("/dashboard")


@app.route('/mark_done/<int:id>')
def mark_done(id):
    record = HealthRecord.query.get(id)
    record.is_done = True
    db.session.commit()
    return redirect('/dashboard')

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # check if user already exists
        existing_user = Caretaker.query.filter(
            (Caretaker.username == username) | (Caretaker.email == email)
        ).first()

        if existing_user:
            return "User or Email already exists!"

        new_user = Caretaker(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect("/")

    return render_template("signup.html")


from datetime import datetime



@app.route('/add_record', methods=['POST'])
def add_record():
    dt_str = request.form.get('datetime')

    if not dt_str:
        return "Please select date and time!"

    dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M")

    print("Job scheduled for:", dt)

    child_id = request.form.get('child_id')
    if child_id:
        child_id = int(child_id)
    
    # Verify child exists
    child = Child.query.get(child_id)
    if not child:
        flash(f"Error: Child with ID {child_id} does not exist. Please register the child first.", "danger")
        return redirect('/dashboard')

    vaccine = request.form.get('vaccination')
    medicine = request.form.get('medicine')
    diagnose = request.form.get('diagnose')
    dosage = request.form.get('dosage')

    # Logic: if vaccination is provided, use it as medicine and set defaults
    if vaccine and not medicine:
        medicine = vaccine
        if not diagnose:
            diagnose = "Vaccination"
        if not dosage:
            dosage = "Standard"
    
    # Fallback defaults if still missing
    if not diagnose: diagnose = "General Checkup"
    if not dosage: dosage = "As prescribed"

    if not medicine:
        flash("Error: Please provide either a medicine name or a vaccination name.", "danger")
        return redirect('/dashboard')

    record = HealthRecord(
        child_id=child_id,
        diagnose=diagnose,
        medicine=medicine,
        dosage=dosage,
        datetime=dt
    )

    db.session.add(record)
    db.session.commit()

    scheduler.add_job(
        func=send_reminder,
        trigger='date',
        run_date=dt,
        args=[request.form['child_id'], request.form['medicine']]
    )

    return redirect('/dashboard')


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


@app.route('/delete_record/<int:id>')
def delete_record(id):
    record = HealthRecord.query.get(id)
    if record:
        db.session.delete(record)
        db.session.commit()
    return redirect('/dashboard')

@app.route('/delete_child/<int:id>')
def delete_child(id):
    child = Child.query.get(id)
    if child:
        # Cascading delete: Remove associated records and medicines
        Medicine.query.filter_by(child_id=id).delete()
        HealthRecord.query.filter_by(child_id=id).delete()
        
        db.session.delete(child)
        db.session.commit()
        flash(f"Child {child.name} and all their records have been deleted.", "success")
    return redirect('/dashboard')

@app.route('/child/<int:id>')
def child_detail(id):
    child = Child.query.get(id)
    records = HealthRecord.query.filter_by(child_id=id).all()

    return render_template(
        'child_detail.html',
        child=child,
        records=records
    )
# RUN
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
