# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask.json import jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload, relationship
from sqlalchemy import ForeignKey
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, IntegerField, SelectField
from wtforms.validators import DataRequired

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
    body = db.Column(db.Text, nullable=True)
    sent_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    type = db.Column(db.String(255), nullable=True)
    invoice_number = db.Column(db.Integer, db.ForeignKey('delivery_notes.id'), nullable=True)
    # Define relationships
    sender = relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    recipient = relationship('User', foreign_keys=[recipient_id], backref='received_messages')
    invoice = relationship('DeliveryNotes', foreign_keys=[invoice_number], backref='invoices')

# Define the Record model
class EntryRecord(db.Model):
    __tablename__ = 'entry_records'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    purpose = db.Column(db.String(255), nullable=False)
    rank = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    patronymic = db.Column(db.String(255), nullable=False)


class DeliveryNotes(db.Model):
    __tablename__ = 'delivery_notes'
    id = db.Column(db.Integer, primary_key=True)
    date_valid_until = db.Column(db.String(20))
    invoice_number = db.Column(db.String(50))
    military_unit_number = db.Column(db.String(50))
    registration_number = db.Column(db.String(50))
    document_number = db.Column(db.String(50))
    document_date = db.Column(db.String(20))
    operation_purpose = db.Column(db.String(255))
    operation_date = db.Column(db.String(20))
    support_service = db.Column(db.String(255))
    military_property_name = db.Column(db.String(255))
    nomenclature_code = db.Column(db.String(50))
    unit_of_measure = db.Column(db.String(50))
    category = db.Column(db.String(50))
    operation_type = db.Column(db.String(50))
    issued_received = db.Column(db.String(50))
    note = db.Column(db.Text)
    submitted = db.Column(db.Boolean, default=False)


# Define the WriteDeliveryForm
class WriteDeliveryForm(FlaskForm):
    date_valid_until = DateField('Дата дійсна до', validators=[DataRequired()])
    invoice_number = StringField('Номер накладної', validators=[DataRequired()])
    military_unit_number = StringField('Номер військової частини', validators=[DataRequired()])
    registration_number = StringField('Номер реєстрації', validators=[DataRequired()])
    document_number = StringField('Номер документа', validators=[DataRequired()])
    document_date = DateField('Дата документа', validators=[DataRequired()])
    operation_purpose = StringField('Мета операції', validators=[DataRequired()])
    operation_date = DateField('Дата операції', validators=[DataRequired()])
    support_service = StringField('Служба забезпечення', validators=[DataRequired()])
    military_property_name = StringField('Назва військового майна', validators=[DataRequired()])
    nomenclature_code = StringField('Код номенклатури', validators=[DataRequired()])
    unit_of_measure = StringField('Одиниця виміру', validators=[DataRequired()])
    category = StringField('Категорія(сорт)', validators=[DataRequired()])
    operation_type = StringField('Видати (прийняти)', validators=[DataRequired()])
    issued_received = StringField('Відпущено(прийняти)', validators=[DataRequired()])
    note = StringField('Примітка')


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

        return render_template('profile.html', user=user, received_messages=received_messages,
                               sent_messages=sent_messages)
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
    if user:
        render_template('write.html', user=user)
    else:
        return redirect(url_for('login'))

    """if request.method == 'POST':
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
            flash('Wrong recipient.', 'error')"""

    return render_template('write.html', user=user)


@app.route('/write_address', methods=['GET', 'POST'])
def write_address():
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

            new_message = Message(sender_id=user[0], recipient_id=recipient_id, subject=subject, body=body,
                                  type=email_type)
            db.session.add(new_message)
            db.session.commit()

            return redirect(url_for('sent'))
        else:
            # User not found, display an error message
            flash('Wrong recipient.', 'error')
    return render_template('write_address.html', user=user)


@app.route('/write_order', methods=['GET', 'POST'])
def write_order():
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

            new_message = Message(sender_id=user[0], recipient_id=recipient_id, subject=subject, body=body,
                                  type=email_type)
            db.session.add(new_message)
            db.session.commit()

            return redirect(url_for('sent'))
        else:
            # User not found, display an error message
            flash('Wrong recipient.', 'error')
    return render_template('write_order.html', user=user)


@app.route('/write_report', methods=['GET', 'POST'])
def write_report():
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
            email_type = "Наказ"  # Get the selected email type

            new_message = Message(sender_id=user[0], recipient_id=recipient_id, subject=subject, body=body,
                                  type=email_type)
            db.session.add(new_message)
            db.session.commit()

            return redirect(url_for('sent'))
        else:
            # User not found, display an error message
            flash('Wrong recipient.', 'error')
    return render_template('write_report.html', user=user)


@app.route('/write_follow_letter', methods=['GET', 'POST'])
def write_follow_letter():
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

            new_message = Message(sender_id=user[0], recipient_id=recipient_id, subject=subject, body=body,
                                  type=email_type)
            db.session.add(new_message)
            db.session.commit()

            return redirect(url_for('sent'))
        else:
            # User not found, display an error message
            flash('Wrong recipient.', 'error')
    return render_template('write_follow_letter.html', user=user)


# Autocomplete recipient route
@app.route('/autocomplete_recipient', methods=['GET'])
def autocomplete_recipient():
    search_term = request.args.get('term')
    department_number = request.args.get('department_number')

    # Exclude the current user from the suggestions
    matching_users = User.query \
        .filter(User.department_number == department_number, User.full_name.ilike(f'%{search_term}%'),
                User.id != session['user'][0]) \
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


@app.route('/get_smth')
def get_smth():
    user = session.get('user')

    if user:
        return render_template('get_smth.html', user=user)
    else:
        return redirect(url_for('login'))


@app.route('/get_flow')
def get_flow():
    user = session.get('user')

    if user:
        return render_template('get_flow.html', user=user)
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


@app.route('/write_delivery', methods=['GET', 'POST'])
def write_delivery():
    form = WriteDeliveryForm()
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
            email_type = "Накладна"  # Get the selected email type

            if form.validate_on_submit():
                delivery_note = DeliveryNotes(
                    date_valid_until=form.date_valid_until.data,
                    invoice_number=form.invoice_number.data,
                    military_unit_number=form.military_unit_number.data,
                    registration_number=form.registration_number.data,
                    document_number=form.document_number.data,
                    document_date=form.document_date.data,
                    operation_purpose=form.operation_purpose.data,
                    operation_date=form.operation_date.data,
                    support_service=form.support_service.data,
                    military_property_name=form.military_property_name.data,
                    nomenclature_code=form.nomenclature_code.data,
                    unit_of_measure=form.unit_of_measure.data,
                    category=form.category.data,
                    operation_type=form.operation_type.data,
                    issued_received=form.issued_received.data,
                    note=form.note.data
                )

                db.session.add(delivery_note)
                db.session.commit()

                new_message = Message(sender_id=user[0], recipient_id=recipient_id, subject=subject, type=email_type, invoice_number=delivery_note.id)
                db.session.add(new_message)
                db.session.commit()

            return redirect(url_for('sent'))
        else:
            # User not found, display an error message
            flash('Wrong recipient.', 'error')
    return render_template('write_delivery.html', form=form, user=user)


@app.route('/edit_delivery/<int:delivery_id>', methods=['GET', 'POST'])
def edit_delivery(delivery_id):
    delivery_note = DeliveryNotes.query.get(delivery_id)
    form = WriteDeliveryForm(obj=delivery_note)

    if form.validate_on_submit():
        form.populate_obj(delivery_note)
        db.session.commit()

        flash('Delivery note updated successfully!', 'success')
        return redirect(url_for('edit_delivery', delivery_id=delivery_id))

    return render_template('edit_delivery.html', form=form, delivery_note=delivery_note)

@app.route('/submit_signature', methods=['POST'])
def submit_signature():
    delivery_id = request.form.get('delivery_id')
    delivery_note = DeliveryNotes.query.get(delivery_id)

    # Toggle the 'submitted' status
    delivery_note.submitted = not delivery_note.submitted
    db.session.commit()

    flash('Signature submitted successfully!', 'success')
    return redirect(url_for('edit_delivery', delivery_id=delivery_id))


# Custom filter to format dates in templates
@app.template_filter('format_date')
def format_date(value, format='%d %B %Y'):
    return value.strftime(format)

@app.route('/record_delivery_notes')
def record_delivery_notes():
    user = session.get('user')

    if user:
        # Fetch all records from the entry_records table
        all_records = (
            DeliveryNotes.query
            .join(Message, DeliveryNotes.id == Message.invoice_number)  # Join with the 'messages' table
            .join(User, User.id == Message.sender_id)  # Join with the 'users' table for sender's full_name\
            .filter(Message.recipient_id == user[0])
            .add_columns(User.full_name, DeliveryNotes.id, DeliveryNotes.date_valid_until, DeliveryNotes.invoice_number, DeliveryNotes.military_unit_number, DeliveryNotes.military_property_name)
            .all()
        )

        return render_template('record_delivery_notes.html', user=user, records=all_records)
    else:
        return redirect(url_for('login'))


@app.route('/record_book_entry')
def record_book_entry():
    user = session.get('user')

    if user:
        # Fetch all records from the entry_records table
        all_records = EntryRecord.query.all()

        return render_template('record_book_entry.html', user=user, records=all_records)
    else:
        return redirect(url_for('login'))


@app.route('/add_record', methods=['GET', 'POST'])
def add_record():
    user = session.get('user')

    if user:
        if request.method == 'POST':
            # Retrieve data from the form
            date = request.form.get('date')
            time = request.form.get('time')
            purpose = request.form.get('purpose')
            rank = request.form.get('rank')
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            patronymic = request.form.get('patronymic')

            new_entry = EntryRecord(date=date, time=time,
                                    purpose=purpose, rank=rank, first_name=first_name, last_name=last_name,
                                    patronymic=patronymic)
            # new_record = Record(date='2023-01-01', time='12:00:00', purpose='Test', rank='Captain', first_name='John', last_name='Doe', patronymic='Smith')
            db.session.add(new_entry)
            db.session.commit()

            # Redirect the user back to the record book entry page
            return redirect(url_for('record_book_entry'))

        return render_template('add_record.html', user=user)
    else:
        return redirect(url_for('login'))


@app.route('/record_numbered')
def record_numbered():
    user = session.get('user')

    if user:
        return render_template('record_numbered.html', user=user)
    else:
        return redirect(url_for('login'))


@app.route('/nakladna', methods=['GET', 'POST'])
def nakladna():
    form = WriteDeliveryForm()
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
            email_type = "Накладна"  # Get the selected email type

            if form.validate_on_submit():
                delivery_note = DeliveryNotes(
                    date_valid_until=form.date_valid_until.data,
                    invoice_number=form.invoice_number.data,
                    military_unit_number=form.military_unit_number.data,
                    registration_number=form.registration_number.data,
                    document_number=form.document_number.data,
                    document_date=form.document_date.data,
                    operation_purpose=form.operation_purpose.data,
                    operation_date=form.operation_date.data,
                    support_service=form.support_service.data,
                    military_property_name=form.military_property_name.data,
                    nomenclature_code=form.nomenclature_code.data,
                    unit_of_measure=form.unit_of_measure.data,
                    category=form.category.data,
                    operation_type=form.operation_type.data,
                    issued_received=form.issued_received.data,
                    note=form.note.data
                )

                db.session.add(delivery_note)
                db.session.commit()

                new_message = Message(sender_id=user[0], recipient_id=recipient_id, subject=subject, type=email_type, invoice_number=delivery_note.id)
                db.session.add(new_message)
                db.session.commit()

            return redirect(url_for('sent'))
        else:
            # User not found, display an error message
            flash('Wrong recipient.', 'error')
    return render_template('nakladna.html', form=form, user=user)


@app.route('/categorical_record')
def categorical_record():
    user = session.get('user')

    if user:
        return render_template('categorical_record.html', user=user)
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
