def get_doctor_appointments_query(doctor_id):
    query = "SELECT * FROM appointments " \
            "WHERE doctor_id = {} ".format(doctor_id)

    return query


def get_appointments_query(date=None):
    query = "SELECT * FROM appointments "
    if date is not None:
        query += "WHERE date(date) = date({})".format(date)

    return "SELECT * FROM appointments"

