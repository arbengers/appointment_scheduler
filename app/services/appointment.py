def get_appointment_data(db, appointment_id):
    query = "SELECT * FROM appointments WHERE id = ?"
    cursor = db.cursor()
    res = cursor.execute(query, (appointment_id,))
    res = res.fetchone()

    return res


def get_curr_total_accepted_appointments(db):
    cursor = db.cursor()
    query = 'SELECT * FROM appointments ' \
            'WHERE date(schedule_time) = CURRENT_DATE ' \
            'AND is_accepted = 1'

    results = cursor.execute(query).fetchall()
    results = [dict(row) for row in results]

    return len(results)

