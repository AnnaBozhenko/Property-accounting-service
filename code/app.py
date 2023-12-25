# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask.json import jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload, relationship
from sqlalchemy import ForeignKey


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# PostgreSQL configuration
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'defense_sys'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    military_id = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    department_number = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# Define the Message model
class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    type = db.Column(db.String(255), nullable=True)
    # Define relationships
    sender = relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    recipient = relationship('User', foreign_keys=[recipient_id], backref='received_messages')


@app.route('/')
def home():
    user = session.get('user')

    if user:
        return redirect(url_for('profile'))
    else:
        return redirect(url_for('login'))
# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        military_id = request.form['military_id']
        full_name = request.form['full_name']
        title = request.form['title']
        department_number = request.form['department_number']
        email = request.form['email']
        password = request.form['password']

        new_user = User(military_id=military_id, full_name=full_name, title=title,
                        department_number=department_number, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('signup.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email, password=password).first()

        if user:
            session['user'] = (user.id, user.military_id, user.full_name, user.title, user.department_number)
            return redirect(url_for('profile'))
        else:
            # User not found, display an error message
            flash('Incorrect email or password. Please try again.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

# Profile route
@app.route('/profile')
def profile():
    user = session.get('user')

    if user:
        received_messages = Message.query.filter_by(recipient_id=user[0]).all()
        sent_messages = Message.query.filter_by(sender_id=user[0]).all()

        return render_template('profile.html', user=user, received_messages=received_messages, sent_messages=sent_messages)
    else:
        return redirect(url_for('login'))

# Logout route
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# Inbox route
@app.route('/inbox')
def inbox():
    user = session.get('user')

    if user:
        received_messages = Message.query.filter_by(recipient_id=user[0]).all()

        return render_template('inbox.html', user=user, received_messages=received_messages)
    else:
        return redirect(url_for('login'))

# Sent route
@app.route('/sent')
def sent():
    user = session.get('user')

    if user:
        sent_messages = Message.query.filter_by(sender_id=user[0]).all()

        return render_template('sent.html', user=user, sent_messages=sent_messages)
    else:
        return redirect(url_for('login'))

# Compose route
@app.route('/compose', methods=['GET', 'POST'])
def compose():
    user = session.get('user')

    if request.method == 'POST':
        department_number = request.form['department_number']  # Corrected line
        recipient_name = request.form['recipient_name']

        # Query only the id of the user based on department number and recipient name
        recipient_id = User.query \
            .filter(User.department_number == department_number, User.full_name == recipient_name) \
            .with_entities(User.id) \
            .scalar()

        if recipient_id:
            subject = request.form['subject']
            body = request.form['body']
            email_type = request.form['email_type']  # Get the selected email type

            new_message = Message(sender_id=user[0], recipient_id=recipient_id, subject=subject, body=body, type=email_type)
            db.session.add(new_message)
            db.session.commit()

            return redirect(url_for('sent'))
        else:
            # User not found, display an error message
            flash('Wrong recipient.', 'error')

    return render_template('compose.html', user=user)

# Autocomplete recipient route
@app.route('/autocomplete_recipient', methods=['GET'])
def autocomplete_recipient():
    search_term = request.args.get('term')
    department_number = request.args.get('department_number')
    
    # Exclude the current user from the suggestions
    matching_users = User.query \
        .filter(User.department_number == department_number, User.full_name.ilike(f'%{search_term}%'), User.id != session['user'][0]) \
        .all()
    
    names = [user.full_name for user in matching_users]
    return jsonify(names)

@app.route('/get_email_detail/<int:message_id>')
def get_email_detail(message_id):
    # Fetch the email details based on the message_id
    message = Message.query.get(message_id)
    sender = User.query.get(message.sender_id)

    # Fetch recipient details
    recipient = User.query.get(message.recipient_id)

    # Render a template with the email details
    return render_template('email_detail.html', message=message, sender=sender, recipient=recipient)


# Add this route to your Flask app
@app.route('/create')
def create():
    user = session.get('user')

    if user:
        return render_template('create.html', user=user)
    else:
        return redirect(url_for('login'))


# Add this route to your Flask app
@app.route('/issue')
def issue():
    user = session.get('user')

    if user:
        return render_template('issue.html', user=user)
    else:
        return redirect(url_for('login'))


# Add this route to handle the "Підрозділу" section
@app.route('/department_process')
def department_process():
    user = session.get('user')

    if user:
        return render_template('department_process.html', user=user)
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
