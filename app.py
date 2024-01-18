from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask import flash
from flask_socketio import SocketIO, emit
from datetime import datetime
import time


app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisisasecret'
socketio = SocketIO(app)

# login manager to manage user sessions
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

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
    major1= db.Column(db.String(50))
    major2 = db.Column(db.String(50))


# The constructor takes in arguments such as fname, lname, and 
# email and assigns them to instance variables with the same names.
    def __init__(self, fname, lname, email, username, password, dob, major1, major2):
        self.fname = fname
        self.lname = lname
        self.email = email
        self.username = username
        self.password = password
        self.dob = dob
        self.major1 = major1
        self.major2 = major2
        
# The class Task inherits from the class Model in the module db.
class Task(db.Model):
    __tablename__ = 'tasks'
    task_id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(50))
    subject = db.Column(db.String(50))
    due_date = db.Column(db.Date)
    estimated_time = db.Column(db.Integer)
    task_percentage = db.Column(db.Integer)
    description = db.Column(db.String(100))
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    priority = db.Column(db.Integer)
    student = db.relationship('Student', backref=db.backref('tasks', lazy=True))

# Constructor method for Task class to create new task objects
    def __init__(self, task_name, subject, due_date, estimated_time, task_percentage, description, student_id, priority):
        self.task_name = task_name
        self.subject = subject
        self.due_date = due_date
        self.estimated_time = estimated_time
        self.task_percentage = task_percentage
        self.description = description
        self.student_id = student_id
        self.priority = priority

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

# 6 queues, 1 for each possible priority
priority_0 = []
priority_1 = []
priority_2 = []
priority_3 = []
priority_4 = []
priority_5 = []

#### Algorithm for MLFQ priority queue ####

# adds all priority queues to a list and returns it
def all_priority(priority_0, priority_1, priority_2, priority_3, priority_4, priority_5):
    all_priority = []
    all_priority.append(priority_5)
    all_priority.append(priority_4)
    all_priority.append(priority_3)
    all_priority.append(priority_2)
    all_priority.append(priority_1)
    all_priority.append(priority_0)
    return all_priority

# finds the highest non-empty priority queue and returns it
def max_priority(all_priority):
    max_priority = []
    for priority in all_priority:
        if priority:
            for item in priority:
                max_priority.append(item)
                print("max_priority: ", max_priority)
            return max_priority

# finds the second non-empty priority queue and returns it
def middle_priority(all_priority):
    middle_priority = []
    counter = 0
    for priority in all_priority:
        if priority:
            counter += 1
            if counter == 2:
                for item in priority:
                    middle_priority.append(item)
                    print("middle_priority: ", middle_priority)
                return middle_priority

# finds the remaining non-empty priority queue and returns it
def min_priority(all_priority):
    min_priority = []
    counter = 0
    for priority in all_priority:
        if priority:
            print("test2: ", priority)
            counter += 1
            if counter >= 3:
                for item in priority:
                    min_priority.append(item)
                    print("min_priority: ", min_priority)
    return min_priority

# pops items from a queue to be displayed on the calendar
# once the queue is empty, the queue is filled again

# def run(priority, temp_queue): 
#     if priority:
#         temp_queue.append(priority[0])
#         print("temp_queue: ", temp_queue)
#         new_task = priority.pop(0)
#         print("new_task: ", new_task)

#         return new_task

# def run2(priority, temp_queue):
#     for item in priority:
#         if priority:
#             new_task = run(priority, temp_queue)
            
#     if not priority:
#         for item in temp_queue:
#             priority.append(item)
#         temp_queue.clear()

# def run3(max_priority, middle_priority, min_priority):
#     run2(max_priority)
#     run2(max_priority)
#     run2(middle_priority)
#     run2(max_priority)
#     run2(min_priority)
#     run


#### End of MLFQ Functions ####

# fills queue in regards to task priority
def fill_queue():
    # fetch
    data = Task.query.filter_by(student_id=current_user.id).all()
    # student_id = Student.query.get(current_user.id)
    for item in data:
        if item.priority == 0:
            priority_0.append(item)
        elif item.priority == 1:
            priority_1.append(item)
        elif item.priority == 2:
            priority_2.append(item)
        elif item.priority == 3:
            priority_3.append(item)
        elif item.priority == 4:
            priority_4.append(item)
        elif item.priority == 5:
            priority_5.append(item)

    #### Testing MLFQ Functions ####

    # complete_priority = all_priority(priority_0, priority_1, priority_2, priority_3, priority_4, priority_5)
    # highest_priority = max_priority(complete_priority)
    # second_priority = middle_priority(complete_priority)
    # lowest_priority = min_priority(complete_priority)
    # print("highest priority: ", highest_priority)
    # print("second priority: ", second_priority)
    # print("lowest priority: ", lowest_priority)

    #### Testing Priority Scheduling Functions ####
    high_priority_task(priority_0, priority_1, priority_2, priority_3, priority_4, priority_5)
    run_task()
    return


#### Algorithm for priority scheduling ####

# gets the first task from the highest non empty priority queue
def high_priority_task(priority_0, priority_1, priority_2, priority_3, priority_4, priority_5):
    # if priority 5 is not empty, return the first task, else checks the following priority queues
    if priority_5:
        return priority_5[0]
    elif priority_4:
        return priority_4[0]
    elif priority_3:
        return priority_3[0]
    elif priority_2:
        return priority_2[0]
    elif priority_1:
        return priority_1[0]
    elif priority_0:
        return priority_0[0]
    else:
        return None

def run_task():
    hp_task = high_priority_task(priority_0, priority_1, priority_2, priority_3, priority_4, priority_5)
    if hp_task is not None:
        # get task estimated time
        estimated_time = hp_task.estimated_time
        while estimated_time > 0:
            time.sleep(2)
            estimated_time -= 1
            print(estimated_time)
            print('p:', hp_task.priority)
            # update estimated time with new value
            hp_task.estimated_time = estimated_time
            db.session.commit()
            emit_task_update() # This will emit the update to the front end
            print('priority 4: ', priority_4)
        # remove task from queue
        if hp_task.estimated_time == 0:
            print('hp_task: ', hp_task)
            # db.session.delete(hp_task)
            # db.session.commit()
            if hp_task.priority == 0:
                priority_0.pop(0)
            elif hp_task.priority == 1:
                priority_1.pop(0)
            elif hp_task.priority == 2:
                priority_2.pop(0)
            elif hp_task.priority == 3:
                priority_3.pop(0)
            elif hp_task.priority == 4:
                priority_4.pop(0)
            elif hp_task.priority == 5:
                priority_5.pop(0)
            run_task()
    else:
        print("No task to run")
    
#### End of Priority Scheduling Functions ####

# Calculate priority based on task percentage, subject, and due date
def calculate_priority(task_percentage, subject, due_date):
    # Section of calculate priority based on task percentage
    task_percentage = int(task_percentage)
    priority = 0
    if task_percentage >= 15:
        priority += 2
    elif task_percentage >= 5:
        priority += 1
    else:
        priority += 0
    print(priority)

    # Get student major from registration page
    student_id = Student.query.get(current_user.id)
    student_major = student_id.major1
    student_major2 = student_id.major2
    student_major = clean_text(student_major)
    student_major2 = clean_text(student_major2)
    subject = clean_text(subject)
    # Section of calculate priority based on subject
    if student_major == subject or student_major2 == subject:
        priority += 1
    else:
        priority += 0
    print(priority)

    # due_date = datetime.strptime(task_data['due_date'], '%Y-%m-%d')  # Assuming due_date is in YYYY-MM-DD format
    current_date = datetime.now()
    due_date = datetime.strptime(due_date, '%Y-%m-%d')
    days_until_due = (due_date - current_date).days
    # Section of calculate priority based on due date
    if days_until_due > -1 and days_until_due <= 1:
        priority += 2
    elif days_until_due > 1 and days_until_due <= 3:
        priority += 1
    else:
        priority += 0
    return priority

def emit_task_update():
    current_task = high_priority_task(priority_0, priority_1, priority_2, priority_3, priority_4, priority_5)
    if current_task:
        socketio.emit('task_update', {
            'task_name': current_task.task_name,
            'estimated_time': current_task.estimated_time,
            'priority': current_task.priority
        })
    else:
        socketio.emit('task_update', {'error': 'No tasks available!'})


@socketio.on('start_task')
def handle_start_task():
    fill_queue()
    run_task()  # Start the task scheduling when the event is received.

@app.route('/get_current_task')
def get_current_task():
    # Your code to fetch the current task
    current_task = high_priority_task(priority_0, priority_1, priority_2, priority_3, priority_4, priority_5)
    if current_task:
        return jsonify({'task_name': current_task.task_name, 'estimated_time': current_task.estimated_time, 'priority': current_task.priority})
    return jsonify({'error': 'No tasks available!'})

@app.route('/scheduler')
def scheduler():
    hp_task = high_priority_task(priority_0, priority_1, priority_2, priority_3, priority_4, priority_5)
    
    if hp_task:
        task_name = hp_task.task_name or "No task name provided"
        estimated_time = hp_task.estimated_time or "No estimated time provided"
        priority = hp_task.priority or "No priority provided"
    else:
        task_name = "No task available"
        estimated_time = "N/A"
        priority = "N/A"

    upcoming_tasks = priority_0 + priority_1 + priority_2 + priority_3 + priority_4 + priority_5
    if hp_task in upcoming_tasks:
        upcoming_tasks.remove(hp_task)  # Exclude the current highest priority task from the upcoming list
    
    return render_template('scheduler.html', output=task_name, estimated_time=estimated_time, priority=priority, upcoming_tasks=upcoming_tasks)


# Clean text to lowercase and remove leading and trailing spaces
def clean_text(text):
    text = text.strip().lower()
    return text

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
    major1 = request.form['major1']
    major2 = request.form['major2']

    # create a new student object and add it to the database
    student = Student(fname, lname, email, username, password, dob, major1, major2)
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
        return redirect(url_for('show_tasks'))
    else:
        # if the username and password are incorrect, display an error message
        error = 'Invalid username or password'
        return render_template('login.html', error=error)

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
    priority = calculate_priority(task_percentage, subject, due_date)

# create a new task object and add it to the database
    tasks = Task(task_name, subject, due_date, estimated_time, task_percentage, description, student_id, priority)
    tasks.student = current_user
    db.session.add(tasks)
    db.session.commit()

    return redirect(url_for('show_tasks'))

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

@app.route('/update-task/<int:task_id>', methods=['POST'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    task.task_name = data.get('Name', task.task_name)
    task.subject = data.get('Subject', task.subject)
    # task.due_date = data.get('due_date', task.due_date)
    # task.estimated_time = data.get('estimated_time', task.estimated_time)
    # task.task_percentage = data.get('task_percentage', task.task_percentage)
    task.description = data.get('Description', task.description)
    
    db.session.commit()
    
    return jsonify({'message': 'Task updated successfully'})

@app.route('/get_task_data/<int:task_id>')
def get_task_data(task_id):
    task = Task.query.get(task_id)
    return jsonify({
        'name': task.task_name,
        'subject': task.subject,
        'description': task.description
    })

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
    socketio.run(app, debug=True) 
    # WARNING: This is a development server. Do not use it in a production deployment. 
    # Use a production WSGI server instead. Check later cause might need to switch servers

    