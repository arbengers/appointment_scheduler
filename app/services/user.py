def get_user_data(db, user_id):
    query = "SELECT * FROM user WHERE id = ?"
    cursor = db.cursor()
    res = cursor.execute(query, (user_id,))
    res = res.fetchone()

    return res


def get_doctor_curr_total_appointments(db):
    cursor = db.cursor()
    query = 'SELECT * FROM appointments ' \
            'WHERE date(schedule_time) = CURRENT_DATE '

    results = cursor.execute(query).fetchall()
    results = [dict(row) for row in results]

    return len(results)


def get_doctor_curr_total_accepted_appointments(db, doctor_id):
    cursor = db.cursor()
    query = 'SELECT * FROM appointments ' \
            'WHERE doctor_id = ? ' \
            'AND date(schedule_time) = CURRENT_DATE ' \
            'AND is_accepted = 1'
    results = cursor.execute(query, (doctor_id,)).fetchall()
    results = [dict(row) for row in results]

    return len(results)

