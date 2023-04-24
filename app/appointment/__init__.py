from flask import Blueprint, request, jsonify, g
from app.db import get_db
from app.middleware.auth import token_required
from app.services.appointment import get_appointment_data, get_curr_total_accepted_appointments
from app.services.user import get_user_data, get_doctor_curr_total_appointments, \
    get_doctor_curr_total_accepted_appointments
from .controller import get_doctor_appointments_query, get_appointments_query
from .validation import *
import copy

bp_routers = Blueprint('appointments', __name__)


@bp_routers.route("/appointment", methods=['GET'])
@token_required
def get_appointment():
    """
        For getting appointment details
        args: appointment_id, doctor_id
        doctor_id: Appointment details for this specific doctor
    """
    db = get_db()
    args = request.args
    appointment_id = args.get("appointment_id", default=None, type=int)
    doctor_id = args.get("doctor_id", default=None, type=int)

    appointment_data = get_appointment_data(db, appointment_id)
    if appointment_data is None:
        return jsonify({
            'data': {'appointment_id': appointment_id},
            'status': 'Fail',
            'message': f"Appointment {appointment_id} not exists"
        }), 404

    # For doctors this route is not available
    # if the login doctor id and passed doctor_id not matched
    if doctor_id is not None:
        if appointment_data['doctor_id'] != doctor_id:
            return jsonify({
                'data': {
                    'appointment_id': appointment_id,
                    'doctor_id': doctor_id
                },
                'status': 'Fail',
                'message': "UnAuthorized Doctor"
            }), 401
    else:
        # For login doctor and no passed doctor_id
        if g.auth_data['level_id'] == 2:
            return jsonify({
                'status': 'Fail',
                'message': 'UnAuthorized user'
            }), 401

    return jsonify({
        'data': dict(appointment_data),
        'status': 'OK',
        'message': 'Successfully retrieve appointment data'
    }), 200


@bp_routers.route("/appointments", methods=['GET'])
@token_required
def get_appointments():
    """
        For Getting List of Appointments
        args: doctor_id
        doctor_id: List of available appointments for this specific doctor

        filters: date
    """
    db = get_db()
    cursor = get_db().cursor()
    args = request.args
    doctor_id = args.get("doctor_id", default=None, type=int)
    date = args.get("date", default=None, type=str)
    query = get_appointments_query(date)
    if doctor_id is not None:
        if get_user_data(db, doctor_id) is None:
            return jsonify({
                'data': {'doctor_id': doctor_id},
                'status': 'Fail',
                'message': f"Doctor {doctor_id} not exists"
            }), 404
        query = get_doctor_appointments_query(doctor_id)
    else:
        # For login doctor and no passed doctor_id
        if g.auth_data['level_id'] == 2:
            return jsonify({
                'status': 'Fail',
                'message': 'UnAuthorized user'
            }), 401

    appointments = cursor.execute(query).fetchall()
    appointments = [dict(row) for row in appointments]

    return jsonify({
        'data': appointments,
        'status': 'OK',
        'message': 'Successfully retrieve appointments data'
    }), 200


@bp_routers.route("/appointment", methods=['POST'])
@token_required
def create_appointment():
    """
        For creating appointments
    """
    # This route is not available for doctor
    if g.auth_data['level_id'] == 2:
        return jsonify({
            'status': 'Fail',
            'message': 'UnAuthorized user'
        }), 401

    data = request.get_json()
    db = get_db()
    cursor = db.cursor()
    validation_results = validate_appointment_data(data)
    if validation_results is not None:
        return jsonify({
            'data': data,
            'status': 'Fail',
            'message': validation_results
        }), 404
    # By default appointment not need to have assigned doctor
    data.setdefault('doctor_id', None)

    # Checking if appointment time is within 9AM - 5PM and not in the past
    if not validate_appointment_schedule(data["schedule_time"]):
        return jsonify({
            'data': data,
            'status': 'Fail',
            'message': 'Appointment schedule is not within opening schedule Monday-Saturday (9AM-5PM) & not in the past'

        }), 404
    # Checking if patient's appointment not overlapping
    validation_results = validate_patient_appointments_schedule(db, data["patient_name"], data["schedule_time"])
    if validation_results is not None:
        return jsonify({
            'data': data,
            'status': 'Fail',
            'message': validation_results
        }), 404

    if data['doctor_id'] is not None:
        # Checking if doctor exists and available
        validation_results = validate_doctor_status(db, data["doctor_id"])
        if validation_results is not None:
            return jsonify({
                'data': data,
                'status': 'Fail',
                'message': validation_results
            }), 404
        # Checking if doctor's appointments not overlapping
        validation_results = validate_doctor_appointments_schedule(db, data["doctor_id"], data["schedule_time"])
        if validation_results is not None:
            return jsonify({
                'data': data,
                'status': 'Fail',
                'message': validation_results
            }), 404
        # Checking if doctor is over-booked
        if get_doctor_curr_total_appointments(db) > 5:
            return jsonify({
                'data': data,
                'status': 'Fail',
                'message': 'The doctor is currently over-booked'
            }), 404

    query = "INSERT INTO appointments (patient_name, schedule_time, doctor_id) VALUES (?, ?, ?)"
    cursor.execute(query, (data["patient_name"], data["schedule_time"], data["doctor_id"]))
    db.commit()

    return jsonify({
            'data': data,
            'status': 'OK',
            'message': 'Successfully created appointment'
        }), 200


@bp_routers.route("/appointment/<appointment_id>", methods=['PATCH'])
@token_required
def update_appointment(appointment_id):
    """
        For updating existing appointment
        Uses overriding in updating appointment data
    """
    # This route is not available for doctor
    if g.auth_data['level_id'] == 2:
        return jsonify({
            'status': 'Fail',
            'message': 'UnAuthorized user'
        }), 401
    data = request.get_json()
    db = get_db()
    cursor = db.cursor()
    appointment_data = get_appointment_data(db, appointment_id)
    if appointment_data is None:
        return jsonify({
            'data': {'appointment_id': appointment_id},
            'status': 'Fail',
            'message': f"Appointment {appointment_id} not exists"
        }), 404
    # SQLITE3 stores boolean values True: 1, False: 0
    # Cannot update appointment once status is accepted
    if appointment_data["is_accepted"] == 1:
        return jsonify({
            'data': {'appointment_id': appointment_id},
            'status': 'Fail',
            'message': f"Cannot Update Accepted Appointments"
        }), 404

    data.setdefault('schedule_time', appointment_data["schedule_time"])
    data.setdefault('patient_name', appointment_data["patient_name"])
    data.setdefault('doctor_id', appointment_data["doctor_id"])
    data.setdefault('is_accepted', appointment_data["is_accepted"])
    # Cater sqlite conversion of boolean, 1 - True, 2 - False
    if data["is_accepted"] == 1:
        data["is_accepted"] = True
        # Checking of total accepted appointments limit, 5
        if get_curr_total_accepted_appointments(db) > 5:
            return jsonify({
                'data': data,
                'status': 'Fail',
                'message': "Appointment acceptance limit"
            }), 404
        # Checking if there's assigned doctor for accepted order
        if data["doctor_id"] is None:
            return jsonify({
                'data': data,
                'status': 'Fail',
                'message': "Cannot accepts an appointment without assigned doctor"
            }), 404
        # Checking if doctor is over-booked
        if get_doctor_curr_total_appointments(db) > 5:
            return jsonify({
                'data': data,
                'status': 'Fail',
                'message': 'The doctor is currently over-booked'
            }), 404
        # Checking of doctor's total accepted appointments limit, 3
        if get_doctor_curr_total_accepted_appointments(db, data["doctor_id"]) > 3:
            return jsonify({
                'data': data,
                'status': 'Fail',
                'message': "Doctor acceptance limit"
            }), 404
    else:
        data["is_accepted"] = False
    # Deep copy, to use in updating appointment data
    _doctor_id = copy.deepcopy(data['doctor_id'])
    # Deleting of doctor_id if it's none before payload validation
    if data["doctor_id"] is None:
        del data["doctor_id"]

    validation_results = validate_appointment_data(data)
    if validation_results is not None:
        return jsonify({
            'data': data,
            'status': 'Fail',
            'message': validation_results
        }), 404
    print(data["schedule_time"])
    print(appointment_data["schedule_time"])
    # Rechecking of patients appointments based on schedule time
    if data["schedule_time"] != appointment_data["schedule_time"]:
        # Checking if appointment schedule is within opening hours
        if not validate_appointment_schedule(data["schedule_time"], update_flag=False):
            return jsonify({
                'data': data,
                'status': 'Fail',
                'message': 'Appointment schedule is not within opening schedule Monday-Saturday (9AM-5PM)'
            }), 404
        validation_results = validate_patient_appointments_schedule(db, data["patient_name"], data["schedule_time"])
        if validation_results is not None:
            return jsonify({
                'data': data,
                'status': 'Fail',
                'message': validation_results
            }), 404
        # Rechecking of doctors appointments based on schedule time
        if data['doctor_id'] is not None:
            validation_results = validate_doctor_status(db, data["doctor_id"])
            if validation_results is not None:
                return jsonify({
                    'data': data,
                    'status': 'Fail',
                    'message': validation_results
                }), 404
            validation_results = validate_doctor_appointments_schedule(db, data["doctor_id"], data["schedule_time"])
            if validation_results is not None:
                return jsonify({
                    'data': data,
                    'status': 'Fail',
                    'message': validation_results
                }), 404

    query = "UPDATE appointments " \
            "SET schedule_time = ?, patient_name = ? , doctor_id = ?, is_accepted = ?" \
            "WHERE id = ?"
    cursor.execute(query, (data["schedule_time"], data["patient_name"], _doctor_id,
                           data["is_accepted"], appointment_id))
    db.commit()

    return jsonify({
        'data': data,
        'status': 'OK',
        'message': 'Successfully updated appointment'
    }), 200


@bp_routers.route("/appointment/<appointment_id>/assign/doctor/<doctor_id>", methods=['PUT'])
@token_required
def assign_doctor(appointment_id, doctor_id):
    """
        For assigning doctor to an appointment
    """
    # This route is not available for doctor
    if g.auth_data['level_id'] == 2:
        return jsonify({
            'status': 'Fail',
            'message': 'UnAuthorized user'
        }), 401

    db = get_db()
    cursor = db.cursor()
    appointment_data = get_appointment_data(db, appointment_id)
    # Checking if appointment exists
    if appointment_data is None:
        return jsonify({
            'data': {'appointment_id': appointment_id},
            'status': 'Fail',
            'message': f"Appointment {appointment_id} not exists"
        }), 404
    # Checking if doctor exists and available
    validation_results = validate_doctor_status(db, doctor_id)
    if validation_results is not None:
        return jsonify({
            'data': {'doctor_id': doctor_id},
            'status': 'Fail',
            'message': validation_results
        }), 404
    # Checking doctor's appointment based on schedule_time
    validation_results = validate_doctor_appointments_schedule(db, doctor_id, appointment_data["schedule_time"])
    if validation_results is not None:
        return jsonify({
            'data': {'doctor_id': doctor_id},
            'status': 'Fail',
            'message': validation_results
        }), 404
    # Checking if doctor is over-booked
    if get_doctor_curr_total_appointments(db) > 5:
        return jsonify({
            'data': {'doctor_id': doctor_id},
            'status': 'Fail',
            'message': 'The doctor is currently over-booked'
        }), 404

    query = "UPDATE appointments " \
            "SET doctor_id = ? "\
            "WHERE id = ?"

    cursor.execute(query, (doctor_id, appointment_id))
    db.commit()

    return jsonify({
        'data': {
            'appointment_id': appointment_id,
            'doctor_id': doctor_id
        },
        'status': 'OK',
        'message': f"Assigning Doctor: {doctor_id} to Appointment {appointment_id} successful"
    }), 200


@bp_routers.route("/activate/doctor/<doctor_id>", methods=['PUT'])
@token_required
def activate_doctor(doctor_id):
    """
        For activating doctor status
    """
    # This route is not available for doctor
    if g.auth_data['level_id'] == 2:
        return jsonify({
            'status': 'Fail',
            'message': 'UnAuthorized user'
        }), 401

    db = get_db()
    cursor = db.cursor()
    # Checking if doctor exists
    if get_user_data(db, doctor_id) is None:
        return jsonify({
            'data': {'doctor_id': doctor_id},
            'status': 'Fail',
            'message': f"Doctor {doctor_id} not exists"
        }), 404

    query = "UPDATE user " \
            "SET status = ? " \
            "WHERE id = ? "
    cursor.execute(query, (True, doctor_id))
    db.commit()

    return jsonify({
        'data': {'doctor_id': doctor_id},
        'status': 'OK',
        'message': f"Doctor: {doctor_id} is now available"
    }), 200


@bp_routers.route("/deactivate/doctor/<doctor_id>", methods=['PUT'])
@token_required
def deactivate_doctor(doctor_id):
    """
        For de-activating doctor status
    """
    # This route is not available for doctor
    if g.auth_data['level_id'] == 2:
        return jsonify({
            'status': 'Fail',
            'message': 'UnAuthorized user'
        }), 401

    db = get_db()
    cursor = db.cursor()
    # Checking if doctor exists
    if get_user_data(db, doctor_id) is None:
        return jsonify({
            'data': {'doctor_id': doctor_id},
            'status': 'Fail',
            'message': f"Doctor {doctor_id} not exists"
        }), 404

    query = "UPDATE user " \
            "SET status = ? " \
            "WHERE id = ? "
    cursor.execute(query, (False, doctor_id))
    db.commit()

    return jsonify({
        'data': {'doctor_id': doctor_id},
        'status': 'OK',
        'message': f"Doctor: {doctor_id} is not available as of now"
    }), 200


@bp_routers.route("/doctor/<doctor_id>/accept/<appointment_id>", methods=['PUT'])
def accepts_appointment(doctor_id, appointment_id):
    """
        For doctor accepting an appointment
    """
    # This route is not available for scheduler
    if g.auth_data['level_id'] == 1:
        return jsonify({
            'status': 'Fail',
            'message': 'UnAuthorized user'
        }), 401

    db = get_db()
    cursor = db.cursor()
    # Checking if doctor exists and available
    validation_results = validate_doctor_status(db, doctor_id)
    if validation_results is not None:
        return jsonify({
            'data': {'doctor_id': doctor_id},
            'status': 'Fail',
            'message': validation_results
        }), 404
    # Checking if doctor that will accepts is assigned to this appointment
    validation_results = validate_doctor_appointment(db, doctor_id, appointment_id)
    if validation_results is not None:
        return jsonify({
            'data': {
                'doctor_id': doctor_id,
                'appointment_id': appointment_id
            },
            'status': 'Fail',
            'message': validation_results
        }), 404
    # Checking of total accepted appointments limit, 5
    if get_curr_total_accepted_appointments(db) > 5:
        return jsonify({
            'data': {
                'appointment_id': appointment_id,
                'doctor_id': doctor_id
            },
            'status': 'Fail',
            'message': "Appointment acceptance limit"
        }), 404

    # Checking of doctor's total accepted appointments limit, 3
    if get_doctor_curr_total_accepted_appointments(db, doctor_id) > 3:
        return jsonify({
            'data': {
                'appointment_id': appointment_id,
                'doctor_id': doctor_id
            },
            'status': 'Fail',
            'message': "Doctor acceptance limit"
        }), 404

    query = "UPDATE appointments " \
            "SET doctor_id = ?, is_accepted = ?" \
            "WHERE id = ? "
    cursor.execute(query, (doctor_id, True, appointment_id))
    db.commit()

    return jsonify({
        'data': {'doctor_id': doctor_id},
        'status': 'OK',
        'message': f"Doctor successfully accepts appointment {appointment_id}"
    }), 200


@bp_routers.route("/appointment/findings", methods=['PUT'])
def set_appointment_findings():
    """
        For doctor accepting an appointment
    """
    # This route is not available for scheduler
    if g.auth_data['level_id'] == 1:
        return jsonify({
            'status': 'Fail',
            'message': 'UnAuthorized user'
        }), 401

    db = get_db()
    cursor = get_db().cursor()
    data = request.get_json()
    # Payload validation
    validation_results = validate_appointment_findings_data(data)
    if validation_results is not None:
        return jsonify({
            'data': data,
            'status': 'Fail',
            'message': validation_results
        }), 404
    # Checking of appointment data exists
    appointment_data = get_appointment_data(db, data['appointment_id'])
    if appointment_data is None:
        return jsonify({
            'data': {'appointment_id': data['appointment_id']},
            'status': 'Fail',
            'message': f"Appointment {data['appointment_id']} not exists"
        }), 404
    # Checking of appointment assigned doctor matched passed doctor_id
    if appointment_data['doctor_id'] != data['doctor_id']:
        return jsonify({
            'data': {
                'appointment_id': data['appointment_id'],
                'doctor_id': data['doctor_id']
            },
            'status': 'Fail',
            'message': "UnAuthorized Doctor"
        }), 401

    query = "UPDATE appointments " \
            "SET comments = ? "\
            "WHERE id = ?"
    cursor.execute(query, (data['comments'], data['appointment_id']))
    db.commit()

    return jsonify({
        'data': data,
        'status': 'OK',
        'message': 'Successfully set appointment findings'
    }), 200


def component_blueprint():
    """
    This returns the component blueprint

    """
    return bp_routers
