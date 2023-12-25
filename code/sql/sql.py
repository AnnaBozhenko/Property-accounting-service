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
    body TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    type VARCHAR(255) NOT NULL
);
'''
cursor.execute(create_messages_table_query)
conn.commit()