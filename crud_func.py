import sqlite3

connection = sqlite3.connect('telegram.db')
cursor = connection.cursor()

def initiate_db():
    cursor.execute('''CREATE TABLE IF NOT EXISTS doctors
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        specialty TEXT NOT NULL,
        experience INTEGER,
        schedule TEXT)
        ''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS services
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL)
        ''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS appointments 
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        doctor_id INTEGER NOT NULL,
        service_id INTEGER NOT NULL,
        datetime TEXT NOT NULL,
        FOREIGN KEY (doctor_id) REFERENCES doctors(id),
        FOREIGN KEY (service_id) REFERENCES services(id))
        ''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS reviews 
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        text TEXT NOT NULL,
        rating INTEGER CHECK (rating BETWEEN 1 AND 5))
        ''')

    connection.commit()

initiate_db()

connection.close()