import json
import datetime
import os
import re

from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import *
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from backend import *
from models import *
from db import Database

ALLOWED_EXTENSIONS = {'png', 'jgp'}

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

        if re.fullmatch("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email) == None:
            flash("Invalid email!", category='error')
            return redirect(url_for('login'))

        user = PatientDBService(app.config).get("email", email, True)

        if user: # if a user is found, we want to redirect back to signup page so user can try again
            if check_password_hash(user.password, password):
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

        elif re.fullmatch("^[a-zA-Z]+", name) == None:
            flash("Invalid name! Use only letters.", category='error')
            return redirect(url_for('signup'))

        elif re.fullmatch("^[0-9]+", phone) == None or len(phone) != 10:
            flash("Invalid phone number! Use 10 numeric digits.", category='error')
            return redirect(url_for('signup'))

        elif re.fullmatch("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email) == None:
            flash("Invalid email!", category='error')
            return redirect(url_for('signup'))

        elif password1 != password2:
            flash('Passwords don\'t match!', category='error')
            return redirect(url_for('signup'))

        else:
            flag, message = checkPass(password1)
            if flag != 0:
                flash(message, category='error')
                return redirect(url_for('signup'))
    

        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        new_user = Patient(-1, name, email, generate_password_hash(password1), phone, None)
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
        try:
            file = request.files['file']
            filename = secure_filename(file.filename)
        except:
            filename = None

        if filename and not allowed_file(filename):
            flash('Invalid profile picture!')
            return redirect(url_for('account'))
        
        form = {key: request.form[key] for key in request.form.keys() if request.form[key] != ''}
        if filename: form.update({'profile_pic': filename})

        data = {key: (form[key] if key in form else current_user.serialize[key]) for key in current_user.serialize.keys()}


        user_exist = PatientDBService(app.config).get("email", data['email']) # if this returns a user, then the email already exists in database
        user_exist = [user for user in user_exist if user.id != current_user.id]
        if user_exist != []: # if a user is found, we want to redirect back to signup page so user can try again
            flash('Email address already in use!', category='error')
            return redirect(url_for('account'))

        elif 'name' in data and re.fullmatch("^[a-zA-Z]+", data['name']) == None:
            flash("Invalid name! Use only letters.", category='error')
            return redirect(url_for('account'))

        elif 'phone' in data and re.fullmatch("^[0-9]+", data['phone']) == None or len(data['phone']) != 10:
            flash("Invalid phone number! Use 10 numeric digits.", category='error')
            return redirect(url_for('account'))

        elif 'email' in data and re.fullmatch("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", data['email']) == None:
            flash("Invalid email!", category='error')
            return redirect(url_for('account'))
        elif ('oldpassword' and 'newpassword1' and 'newpassword2') in data:
            if current_user.password != data['oldpassword']:
                flash('Invalid old password!')
                return redirect(url_for('account'))
            if data['newpassword1'] != data['newpassword2']:
                flash('New passwords don\'t match!')
                return redirect(url_for('account'))

            flag, message = checkPass(data['newpassword1'])
            if flag != 0:
                flash(message, category='error')
                return redirect(url_for('account'))

        db.conn.reconnect()
        cursor = db.conn.cursor(dictionary=True, buffered=True)
        string = "update patients set"
        string += " name='" + data['name']
        string += "', email='" + data['email']
        string += "', password='" + data['password']
        string += "', phone='" + data['phone']
        string += "', profile_pic='" + data['profile_pic']
        string += "' where id=" + str(current_user.id) + ";"
        cursor.execute(string);
        cursor.close()
        db.conn.commit()

        if filename:
            if filename != 'default.png':
                # os.remove(url_for('static', filename="images/profiles/" + current_user.profile_pic))
                if len(file.read()) > 20000000:
                    flash("Profile picture file size too big!")
                    return redirect(url_for('index'))
                
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))    
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
        
        if data < datetime.datetime.now().date():
            flash("That date has already passed!")
            return redirect(url_for('newappointment'))

        new_appointment = Appointment(-1, current_user, doctor, department, data, message)

        AppointmentDBService(app.config).put(new_appointment)
        render_template('appointments.html', user=current_user)

    doctors = DoctorDBService(app.config).get()
    departments = DepartmentDBService(app.config).get()
    return render_template('requestappointment.html',doctors=doctors,departments=departments, user=current_user)

@app.route('/exams/', methods=['GET', 'POST'])
@login_required
def exams():
    if request.method == 'POST':
        examcode = request.form.get('examcode')
        exam = ExamDBService(app.config).get("code", examcode, True)
        
        if current_user.id != exam.patient.id:
            flash('That exam doesn\'t belong to you!')
            return redirect(url_for('exams'))
        return render_template('exams.html', exam=exam, user=current_user)
    
    return render_template('exams.html', user=current_user)


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

# Python program to check validation of password
# Module of regular expression is used with search()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def checkPass(password):
    flag = 0
    message = ""
    if len(password) < 8:
        flag = -1
        message = "Password should be bigger than 8 characters."
    elif re.search("[a-z]", password) == None:
        flag = -1
        message = "Password should have at least one lower case letter."
    elif re.search("[A-Z]", password) == None:
        flag = -1
        message = "Password should have at least one upper case letter."
    elif re.search("[0-9]", password) == None:
        flag = -1
        message = "Password should have at least one number."
    elif re.search("[_@$]", password) == None:
        flag = -1
        message = "Password should have at least one special character (_, @ or $)."
    elif re.search("\s", password) != None:
        flag = -1
        message = "Password shouldn't have whitespaces."

    return flag, message

if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5000")