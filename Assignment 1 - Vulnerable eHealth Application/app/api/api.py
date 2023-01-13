import json

from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import *
import datetime
import os

from backend import *
from models import *
from db import Database

app = Flask(__name__)

app.config.from_file('config.json', load=json.load)
app.config['UPLOAD_FOLDER'] = 'static/images/profiles'

db = Database(app.config)


login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

## AUTHENTICATION METHODS ##

@login_manager.user_loader
def load_user(user_id: int) -> Patient:
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return PatientDBService(app.config).get("id", user_id, True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        db.conn.reconnect()
        cursor = db.conn.cursor(dictionary=True, buffered=True)
        cursor.execute("select * from patients where email = '" + email + "' and password = '" + password + "'")
        user = PatientDBService(app.config).deserialize(cursor.fetchone())
        cursor.close()

        if user: # if a user is found, we want to redirect back to signup page so user can try again
            flash('Logged in successfully!', category='success')
            login_user(user, remember=True)
            return redirect(url_for('index'))
        else:
            flash('Incorrect password, try again!', category='error')
    else:
        flash('Email does not exist.', category='error')

    return render_template('login.html', user=current_user)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # code to validate and add user to database goes here
        email = request.form.get('email')
        name = request.form.get('name')
        phone = request.form.get('phone')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        
        user_exist = PatientDBService(app.config).get("email", email) # if this returns a user, then the email already exists in database

        if user_exist != []: # if a user is found, we want to redirect back to signup page so user can try again
            flash('Email address already in use!', category='error')
            return redirect(url_for('signup'))
        elif password1 != password2:
            flash('Passwords don\'t match!', category='error')
        

        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        new_user = Patient(-1, name, email, password1, phone, None)
        # add the new user to the database
        PatientDBService(app.config).put(new_user)
        login_user(new_user, remember=True)
        flash('Account created with success!', category='success')
        return render_template('login.html', user=current_user)

    return render_template('signup.html', user=current_user)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

## HTML METHODS ##

@app.route('/')
def default():
    return redirect(url_for('index'))

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    if request.method == 'POST':
        pic = request.files['file']
        form = request.form
        user = current_user

        data = {key: user.serialize[key] if key not in form or form[key] == '' else form[key] for key in user.serialize.keys()}

        db.conn.reconnect()
        cursor = db.conn.cursor(dictionary=True, buffered=True)
        string = "update patients set"
        string += " name='" + data['name']
        string += "', email='" + data['email']
        string += "', password='" + data['password']
        string += "', phone='" + data['phone']
        string += "', profile_pic='" + (pic.filename if pic.filename != '' else 'default.png')
        string += "' where id=" + str(data['id']) + ";"
        cursor.execute(string);
        cursor.close()
        db.conn.commit()

        if pic.filename != '': pic.save(os.path.join(app.config['UPLOAD_FOLDER'], pic.filename))
        return redirect(url_for('index'))

    return render_template('profile.html', user=current_user)

@app.route('/index')
def index():
    return render_template('index.html', user=current_user)

@app.route('/appointments/')
@login_required
def appointments():
    appointmentList = AppointmentDBService(app.config).get("patient_id", current_user.id)

    if appointmentList is None or len(appointmentList) == 0:
        return render_template('appointments.html', user=current_user)
    
    return render_template('appointments.html', appointmentList=appointmentList, user=current_user)

@app.route('/newappointment/', methods=['GET', 'POST'])
@login_required
def newappointment():
    if request.method == 'POST':
        department_name = request.form.get('department')
        doctor_name = request.form.get('doctor')
        date_str = request.form.get('date')
        message = request.form.get('message')

        doctor = DoctorDBService(app.config).get("name", doctor_name, True)
        department = DepartmentDBService(app.config).get("name", department_name, True)
        data = datetime.datetime.strptime(str(date_str), "%m/%d/%Y").date()
        
        new_appointment = Appointment(-1, current_user, doctor, department, data, message)

        AppointmentDBService(app.config).put(new_appointment)
        render_template('appointments.html', user=current_user)

    doctors = DoctorDBService(app.config).get()
    departments = DepartmentDBService(app.config).get()
    return render_template('requestappointment.html',doctors=doctors,departments=departments, user=current_user)



@app.route('/exams/', methods=['GET', 'POST'])
def exams():
    if request.method == 'GET':
        return render_template('exams.html', user=current_user)
    elif request.method == 'POST':
        examcode = request.form.get('examcode')
        exam = ExamDBService(app.config).get("code", examcode, True)
        return render_template('exams.html', exam=exam, user=current_user)

@app.route('/blog/', methods=['GET', 'POST'])
def blog():
    if request.method == 'GET':
        comments = CommentDBService(app.config).get()
        return render_template('blog.html', comments=comments, user=current_user)

    elif request.method == 'POST':
        author = request.form.get("author")
        email = request.form.get("email")
        text = request.form.get("comment_text")

        comment = Comment(-1, author, email, text)

        CommentDBService(app.config).put(comment)
        return redirect(url_for('blog'))

@app.route('/team/')
def team():
    return render_template('team.html', user=current_user)

@app.route('/contact/')
def contact():
    return render_template('contact.html', user=current_user)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5000")