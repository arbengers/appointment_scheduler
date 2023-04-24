from jsonschema import validate, ValidationError
from rfc3339_validator import validate_rfc3339
from datetime import datetime, time


def validate_appointment_data(data):
    appointment_schema = {
        "type": "object",
        "properties": {
            "schedule_time": {
                "type": "string",
                "error_msg": "schedule_time must be text"
            },
            "patient_name": {
                "type": "string",
                "error_msg": "patient_name must be text"
            },
            "doctor_id": {
                "type": "number",
                "error_msg": "doctor_id must be number"
            },
            "is_accepted": {
                "type": "boolean",
                "error_msg": "is_accepted must be boolean"
            },
            "comments": {
                "type": "string",
                "error_msg": "comments must be text"
            }
        },
        "required": ["schedule_time", "patient_name"],
    }

    try:
        validate(instance=data, schema=appointment_schema)
    except ValidationError as err:
        return err.schema["error_msg"] if "error_msg" in err.schema else err.message

    if not validate_rfc3339(data["schedule_time"]):
        return "Invalid schedule time format must be UTC"

    return


def validate_appointment_findings_data(data):
    appointment_schema = {
        "type": "object",
        "properties": {
            "appointment_id": {
                "type": "number",
                "error_msg": "appointment_id must be number"
            },
            "doctor_id": {
                "type": "number",
                "error_msg": "doctor_id must be number"
            },
            "comments": {
                "type": "string",
                "error_msg": "comments must be text"
            }
        },
        "required": ["appointment_id", "doctor_id", "comments"],
    }

    try:
        validate(instance=data, schema=appointment_schema)
    except ValidationError as err:
        return err.schema["error_msg"] if "error_msg" in err.schema else err.message

    if not validate_rfc3339(data["schedule_time"]):
        return "Invalid schedule time format must be UTC"

    return


def validate_appointment_schedule(schedule_time, update_flag=True):
    # Removing Z from schedule_time ISO format
    schedule_time = schedule_time.replace('Z', '')
    dt = datetime.fromisoformat(schedule_time)
    # Creating Appointment schedule cannot be in the past
    if update_flag and dt.date() < datetime.now().date():
        return False
    start_time = time(9, 0, 0)
    end_time = time(15, 0, 0)

    # python date().weekday(), if value is 6 == Sunday, system is closed
    return start_time <= dt.time() <= end_time and dt.date().weekday() != 6


def validate_patient_appointments_schedule(db, patient_name, schedule):
    query = 'SELECT * FROM appointments WHERE patient_name = ? AND schedule_time = ?'
    cursor = db.cursor()
    res = cursor.execute(query, (patient_name, schedule))
    res = res.fetchall()
    if len(res) > 1:
        return 'Cannot create an appointment, Patient does have existing appointment on the same time'

    return


def validate_doctor_status(db, doctor_id):
    query = 'SELECT * FROM user ' \
            'WHERE id = ?'
    cursor = db.cursor()
    res = cursor.execute(query, (doctor_id,))
    res = res.fetchone()
    if res is None:
        return f"Doctor with doctorId {doctor_id} not exists"
    # SQLITE3 stores boolean values True: 1, False: 0
    elif res["status"] is 0:
        return f"Doctor {doctor_id} is not available at the moment"

    return


def validate_doctor_appointments_schedule(db, doctor_id, schedule):
    query = 'SELECT * FROM appointments WHERE doctor_id = ? AND schedule_time = ?'
    cursor = db.cursor()
    res = cursor.execute(query, (doctor_id, schedule))
    res = res.fetchall()
    res = [dict(row) for row in res]
    if len(res) > 1:
        return f'Cannot assign the doctorId: {doctor_id} to an appointment, ' \
                                   'Doctor is not available during this time'

    return


def validate_doctor_appointment(db, doctor_id, appointment_id):
    query = 'SELECT * FROM appointments ' \
            'WHERE id = ? ' \
            'AND doctor_id = ?'
    cursor = db.cursor()
    res = cursor.execute(query, (appointment_id, doctor_id))
    res = res.fetchone()
    if res is None:
        return f"UnAuthorized Doctor: This Doctor is not assigned to this appointment"

    return


