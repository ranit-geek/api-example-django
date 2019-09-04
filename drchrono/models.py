from django.db import models
from .options import GENDERS


# Add your models here

class Doctor(models.Model):
    id = models.IntegerField(primary_key=True)

    def __str__(self):
        return str(self.id)


class Patient(models.Model):

    gender = models.CharField(max_length=1, choices=GENDERS, default='Other')
    patient_id = models.IntegerField(unique=True)
    doctor_id = models.IntegerField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return '{} {} ID: {}'.format(self.first_name, self.last_name, str(self.patient_id))


class Appointment(models.Model):
    appointment_id = models.CharField(unique=True, max_length=200)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    check_in_time = models.DateTimeField(auto_now_add=True)
    doctor_id = models.IntegerField()
    wait_time = models.DurationField(null=True)
    status = models.CharField(max_length=200, null=True, default='')

    def __str__(self):
        return '{} {} checked in at {}'.format(self.patient.first_name, self.patient.last_name, str(self.check_in_time))


class AverageWaitTime(models.Model):
    date = models.DateField(primary_key=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    average_wait_time = models.FloatField(default=0)

    def __str__(self):
        return str(self.average_wait_time)
