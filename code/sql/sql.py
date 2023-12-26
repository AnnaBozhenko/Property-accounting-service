import psycopg2

# PostgreSQL configuration
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'defense_sys'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'

# Connect to PostgreSQL
conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
cursor = conn.cursor()

# Function to create the users table if not exists
create_table_query = '''
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    military_id VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    department_number INT NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);
'''
cursor.execute(create_table_query)
conn.commit()

# Add this table creation query to the existing create_users_table function
create_messages_table_query = '''
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    sender_id INT REFERENCES users(id),
    recipient_id INT REFERENCES users(id),
    subject VARCHAR(255) NOT NULL,
    body TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    type VARCHAR(255) NOT NULL,
    invoice_number INT REFERENCES delivery_notes(id),
    folllow_letter_num INT REFERENCES folllow_letter(id)
);
'''
cursor.execute(create_messages_table_query)
conn.commit()

# Function to create the records table if not exists
create_entry_records_table_query = '''
CREATE TABLE IF NOT EXISTS entry_records (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    time TIME NOT NULL,
    purpose VARCHAR(255) NOT NULL,
    rank VARCHAR(255) NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    patronymic VARCHAR(255) NOT NULL
);
'''

# Execute the query and commit the changes
cursor.execute(create_entry_records_table_query)
conn.commit()
create_delivery_notes_table_query = '''
CREATE TABLE delivery_notes (
    id SERIAL PRIMARY KEY,
    date_valid_until DATE,
    invoice_number VARCHAR(255),
    military_unit_number VARCHAR(255),
    registration_number VARCHAR(255),
    document_number VARCHAR(255),
    document_date DATE,
    operation_purpose VARCHAR(255),
    operation_date DATE,
    support_service VARCHAR(255),
    military_property_name VARCHAR(255),
    nomenclature_code VARCHAR(255),
    unit_of_measure VARCHAR(255),
    category VARCHAR(255),
    operation_type VARCHAR(255),
    issued_received VARCHAR(255),
    released_received VARCHAR(255),
    note TEXT,
    submitted BOOLEAN DEFAULT FALSE
);
'''
cursor.execute(create_delivery_notes_table_query)
conn.commit()

create_follow_letter_table_query = '''
CREATE TABLE follow_letter (
    id SERIAL PRIMARY KEY,
    military_property_name VARCHAR(255) NOT NULL,
    sender VARCHAR(255) NOT NULL,
    recipient VARCHAR(255) NOT NULL,
    vehicle_number VARCHAR(255),
    expediter VARCHAR(255),
    order_number VARCHAR(255),
    dispatch_date DATE,
    delivery_date DATE
);
'''
cursor.execute(create_follow_letter_table_query)
conn.commit()
