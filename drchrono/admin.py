from django.contrib import admin

# Register your models here.
from .models import Doctor, AverageWaitTime, Appointment, Patient

# Register your models here.
admin.site.register(Doctor)
admin.site.register(Appointment)
admin.site.register(AverageWaitTime)
admin.site.register(Patient)

