from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask import flash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisisasecret'

# login manager to manage user sessions
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

######## change password to environment variable later ########
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:Hakila3944@localhost:5433/scheduler'

db = SQLAlchemy(app)


# The class Student inherits from the class Model in the module db.
# Table name is students for login and register
class Student(db.Model, UserMixin):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(50))
    lname = db.Column(db.String(50))
    email = db.Column(db.String(100))
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    dob = db.Column(db.DateTime)

# The constructor takes in arguments such as fname, lname, and 
# email and assigns them to instance variables with the same names.
    def __init__(self, fname, lname, email, username, password, dob):
        self.fname = fname
        self.lname = lname
        self.email = email
        self.username = username
        self.password = password
        self.dob = dob

# The class Task inherits from the class Model in the module db.
class Task(db.Model):
    __tablename__ = 'tasks'
    task_id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(50))
    subject = db.Column(db.String(50))
    due_date = db.Column(db.Date)
    estimated_time = db.Column(db.Time)
    task_percentage = db.Column(db.Integer)
    description = db.Column(db.String(100))
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    student = db.relationship('Student', backref=db.backref('tasks', lazy=True))

# Constructor method for Task class to create new task objects
    def __init__(self, task_name, subject, due_date, estimated_time, task_percentage, description, student_id):
        self.task_name = task_name
        self.subject = subject
        self.due_date = due_date
        self.estimated_time = estimated_time
        self.task_percentage = task_percentage
        self.description = description
        self.student_id = student_id

# The class Event inherits from the class Model in the module db.
# class Event(db.Model):
#     __tablename__ = 'events'
#     event_id = db.Column(db.Integer, primary_key=True)
#     event_name = db.Column(db.String(50))
#     subject = db.Column(db.String(50))
#     date = db.Column(db.Date)
#     time_start = db.Column(db.Time)
#     time_end = db.Column(db.Time)
#     repeat = db.Column(db.string(50))
#     description = db.Column(db.String(100))
#     student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
#     student = db.relationship('Student', backref=db.backref('assignments', lazy=True))

# # Constructor method for Event class to create new event objects
#     def __init__(self, event_name, subject, date, time_start, time_end, repeat, description):
#         self.event_name = event_name
#         self.subject = subject
#         self.date = date
#         self.time_start = time_start
#         self.time_end = time_end
#         self.repeat = repeat
#         self.description = description
#         self.student_id = current_user.id

# home page
@app.route('/')
def index():
    return render_template('index.html')

# register page
@app.route('/register')
def registar():
    return render_template('register.html')

# takes in the form data from the register page
@app.route('/submit-register', methods=['POST'])
def submit_register():
    fname = request.form['fname']
    lname = request.form['lname']
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    dob = request.form['dob']

# create a new student object and add it to the database
    student = Student(fname, lname, email, username, password, dob)
    db.session.add(student)
    db.session.commit()

    return render_template('login.html')

@login_manager.user_loader
def load_user(user_id):
    return Student.query.get(int(user_id)) 

# login page
@app.route('/login')
def login():
    return render_template('login.html')

# takes in the form data from the login page, checks user information, takes to dashboard
@app.route('/submit-login', methods=['POST'])
def submit_login():
    error = None
    username = request.form['username']
    password = request.form['password']
    student = Student.query.filter_by(username=username, password=password).first()
    if student is not None:
        # if the username and password are correct, redirect to dashboard
        login_user(student)
        return redirect(url_for('tasks'))
    else:
        # if the username and password are incorrect, display an error message
        error = 'Invalid username or password'
        return render_template('login.html', error=error)

# dashboard page
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# tasks page
@app.route('/add-tasks')
@login_required 
def tasks():
    return render_template('add-tasks.html')

# takes in the form data from the tasks page
@app.route('/submit-task', methods=['POST'])
def submit_tasks():
    task_name = request.form['task_name']
    subject = request.form['subject']
    due_date = request.form['due_date']
    estimated_time = request.form['estimated_time']
    task_percentage = request.form['task_percentage']
    description = request.form['description']
    student_id = current_user.id

# create a new task object and add it to the database
    tasks = Task(task_name, subject, due_date, estimated_time, task_percentage, description, student_id)
    tasks.student = current_user
    db.session.add(tasks)
    db.session.commit()

    return render_template('dashboard.html')

@app.route('/show-tasks')
@login_required
def show_tasks():
    tasks = Task.query.filter_by(student_id=current_user.id).all()
    return render_template('show-tasks.html', tasks=tasks)

@app.route('/delete-task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task_to_delete = Task.query.get_or_404(task_id)
    if task_to_delete.student_id != current_user.id:
        abort(403) # Forbidden, the user is not allowed to delete this task
    db.session.delete(task_to_delete)
    db.session.commit()
    flash('Task has been deleted!', 'success')
    return redirect(url_for('show_tasks'))

# events page
# @app.route('/add-events')
# def events():
#     return render_template('events.html')

# takes in the form data from the events page
# @app.route('/submit-events', methods=['POST'])
# def submit_events():
#     event_name = request.form['event_name']
#     subject = request.form['subject']
#     date = request.form['date']
#     time_start = request.form['time_start']
#     time_end = request.form['time_end']
#     repeat = request.form['repeat']
#     description = request.form['description']

# # create a new event object and add it to the database
#     events = Event(event_name, subject, date, time_start, time_end, repeat, description)
#     db.session.add(events)
#     db.session.commit()

#     return render_template('dashboard.html')

if __name__== "__main__":
    # in production enviroment mark debug as false
    app.run(debug=True) 
    # WARNING: This is a development server. Do not use it in a production deployment. 
    # Use a production WSGI server instead. Check later cause might need to switch servers

    