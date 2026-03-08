import sqlite3

conn = sqlite3.connect("clinic.db", check_same_thread=False)
cursor = conn.cursor()

def create_appointment(name, date, time, reason):

    cursor.execute(
        "INSERT INTO appointments (name, date, time, reason) VALUES (?, ?, ?, ?)",
        (name, date, time, reason)
    )

    conn.commit()

    return "Appointment booked successfully!"
