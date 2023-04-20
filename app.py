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

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
"""
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/submit-login', methods=['POST, GET'])
def submit_login():
    username = request.form['username']
    password = request.form['password']

        # check if the username and password are correct from postgresql
    student = Student.query.filter_by(username=username, password=password).first()
    if student:
        return render_template('dashboard.html')
    else:
        # if the username and password are incorrect return an error message
        return render_template('register.html', error='Invalid username or password')
"""
@app.route('/login')
def login():
    return render_template('login.html')

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
        return render_template('dashboard.html', error=error)





if __name__== "__main__":
    # in production enviroment mark debug as false
    app.run(debug=True) 
    # WARNING: This is a development server. Do not use it in a production deployment. 
    # Use a production WSGI server instead. Check later cause might need to switch servers

    