from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

######## change password to environment variable later ########
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:Hakila3944@localhost:5433/scheduler'

db = SQLAlchemy(app)


# The class Student inherits from the class Model in the module db.
# Table name is students for login and register
class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(50))
    lname = db.Column(db.String(50))
    email = db.Column(db.String(100))
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    dob = db.Column(db.DateTime)

# The constructor takes in three arguments fname, lname, and 
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
    deadline = db.Column(db.DateTime)
    estimated_time = db.Column(db.DateTime)
    task_percentage = db.Column(db.Integer)
    description = db.Column(db.String(100))
    priority = db.Column(db.Integer)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    student = db.relationship('Student', backref=db.backref('tasks', lazy=True))

class Event(db.Model):
    __tablename__ = 'events'
    event_id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(50))
    subject = db.Column(db.String(50))
    date = db.Column(db.DateTime)
    time_start = db.Column(db.DateTime)
    time_end = db.Column(db.DateTime)
    repeat = db.Column(db.string(50))
    description = db.Column(db.String(100))
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    student = db.relationship('Student', backref=db.backref('assignments', lazy=True))


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
        return redirect(url_for('index'))
    else:
        # if the username and password are incorrect, display an error message
        error = 'Invalid username or password'
        return render_template('login.html', error=error)

# dashboard page
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__== "__main__":
    # in production enviroment mark debug as false
    app.run(debug=True) 
    # WARNING: This is a development server. Do not use it in a production deployment. 
    # Use a production WSGI server instead. Check later cause might need to switch servers

    