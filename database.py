import sqlite3
import json


DATABASE_PATH = 'telegram.db'

def get_doctors():
    """Возвращает список врачей."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, specialty FROM doctors")
    doctors = cursor.fetchall()
    conn.close()
    return doctors

def get_services():
    """Возвращает список услуг."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, description FROM services")
    services = cursor.fetchall()
    conn.close()
    return services

def get_reviews():
    """Возвращает список отзывов."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT text, rating FROM reviews")
    reviews = cursor.fetchall()
    conn.close()
    return reviews

def book_appointment(user_id, doctor_id, service_id, datetime):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT schedule FROM doctors WHERE id = ?", (doctor_id,))
        schedule = cursor.fetchone()[0]
        available_slots = json.loads(schedule)
        if datetime in available_slots:
          cursor.execute("INSERT INTO appointments (user_id, doctor_id, service_id, datetime) VALUES (?, ?, ?, ?)",
                         (user_id, doctor_id, service_id, datetime))
          conn.commit()
          return True
        else:
          return False
    except Exception as e:
      print(f"Error booking appointment: {e}")
      return False
    finally:
        conn.close()

def get_available_slots(doctor_id, date):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT schedule FROM doctors WHERE id = ?", (doctor_id,))
        schedule_json = cursor.fetchone()[0]
        try:
            schedule = json.loads(schedule_json)
            available_slots = schedule.get(date, [])
            return available_slots
        except json.JSONDecodeError:
            print(f"Error decoding JSON for doctor {doctor_id}: {schedule_json}")
            return []
    except Exception as e:
        print(f"Error getting available slots: {e}")
        return []
    finally:
        conn.close()

def get_doctor_by_id(doctor_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM doctors WHERE id = ?", (doctor_id,))
        doctor = cursor.fetchone()
        if doctor:
            return dict(zip([description[0] for description in cursor.description], doctor))
        else:
            return None
    except Exception as e:
        print(f"Error getting doctor by ID: {e}")
        return None
    finally:
        conn.close()

def get_service_name(service_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name FROM services WHERE id = ?", (service_id,))
        service_name = cursor.fetchone()
        if service_name:
            return service_name[0]  # Возвращаем только имя услуги
        else:
            return None
    except Exception as e:
        print(f"Error getting service name: {e}")
        return None
    finally:
        conn.close()
