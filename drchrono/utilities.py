from datetime import datetime, timedelta

import pytz

from drchrono.models import Appointment, AverageWaitTime, Doctor


def calculate_average_wait_time(doctor, user_timezone):

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
        return "There is no patient completed"
    total_wait_time = timedelta(0)
    for appointment in appointments:
        total_wait_time = total_wait_time + appointment.wait_time

    avg_seconds = total_wait_time / len(appointments)
    average_obj, created = AverageWaitTime.objects.update_or_create(
        pk=today,
        defaults={
            'doctor': Doctor.objects.get(id=doctor),
            'average_wait_time': int(avg_seconds.total_seconds()/60),
        },
    )
