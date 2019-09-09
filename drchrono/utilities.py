from datetime import datetime, timedelta
import pytz
from drchrono.endpoints import PatientEndpoint, AppointmentEndpoint, DoctorEndpoint
from drchrono.models import Appointment, AverageWaitTime, Doctor, Patient


def calculate_average_wait_time(doctor_id, user_timezone):
    """
    This function calculates today's average wait time of the patients who has completed their session.
    If this function gets called more than once in a day it replaces the calculated time with recently
    calculated time.
    :param doctor_id: Id of the doctor
    :param user_timezone: Local time zone of the user
    :return:

    """
    today = datetime.now(pytz.timezone(user_timezone))
    appointments = Appointment.objects.filter(
        status='Complete',
        check_in_time__isnull=False,
        session_start_time__isnull=False,
        session_start_time__year=today.year,
        session_start_time__month=today.month,
        session_start_time__day=today.day
    )
    if len(appointments) == 0:
        return "No patient have been added to completed state"
    total_wait_time = timedelta(0)
    for appointment in appointments:
        total_wait_time = total_wait_time + appointment.wait_time
    avg_seconds = total_wait_time / len(appointments)
    average_obj, created = AverageWaitTime.objects.update_or_create(
        pk=today,
        defaults={
            'doctor': Doctor.objects.get(id=doctor_id),
            'average_wait_time': int(avg_seconds.total_seconds()/60),
        },
    )


def save_patient(token, patient_id):

    """
    This function saves a patient to the db. If the patient already exists in the records it updates the object.
    :param token: Access token
    :param patient_id: Unique id of the patient
    :return:
    """
    patient = PatientEndpoint(access_token=token).fetch(patient_id)
    patient_object, created = Patient.objects.update_or_create(
        patient_id=patient['id'],
        defaults={
            'gender': patient['gender'],
            'doctor_id': patient['doctor'],
            'first_name': patient['first_name'],
            'last_name': patient['last_name'],
            'email': patient['email'],
            'patient_photo': patient['patient_photo']
        }
    )


def save_appointment(appointment_obj):

    """
    This functions saves a given appointment object.
    :param appointment_obj:  Appointment object
    :return:
    """
    appointment_object, created = Appointment.objects.update_or_create(
        appointment_id=appointment_obj['id'],
        defaults={
            'status': '',
            'patient': Patient.objects.get(patient_id=appointment_obj['patient']),
            'scheduled_time': appointment_obj['time']

        }
    )


def filter_appointments(token, date, status):

    """
    This function fetches all appointments of a given date and filters appointments according to the status provided.
    :param token: Access token
    :param date: Date for which the appointments will be fetched
    :param status: Status of the appointments by which filter will get applied.
    :return: Returns a list of filtered appointments with specific fields.
    """
    appointments = AppointmentEndpoint(access_token=token).list(
        date=date)
    return [
        {
            'id': appointment['id'],
            'patient': appointment['patient'],
            'time': datetime.strptime(appointment['scheduled_time'], "%Y-%m-%dT%H:%M:%S")
        }
        for appointment in appointments
        if appointment['status'] == status
    ]


def save_doctor(token, doctor_id):
    """
    This function fetches the doctor object using the id proved and saves it in the db.
    :param token: Access token
    :param doctor_id: Unique id of a doctor
    :return:
    """
    doctor = DoctorEndpoint(access_token=token).fetch(doctor_id)
    Doctor.objects.get_or_create(id=doctor["id"],
                                 first_name=doctor["first_name"],
                                 last_name=doctor["last_name"],
                                 doctor_photo=doctor["profile_picture"])
