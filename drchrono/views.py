import datetime

from django.contrib.auth.decorators import login_required
import requests
from django.shortcuts import redirect , render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from rest_framework.exceptions import APIException
from social_django.models import UserSocialAuth
from django.views.generic import View
from drchrono.endpoints import DoctorEndpoint, BaseEndpoint, AppointmentEndpoint, PatientEndpoint
from drchrono.forms import PatientCheckInForm, DemographicsForm
from drchrono.models import Appointment, Doctor


def get_token():
    """
    Social Auth module is configured to store our access tokens. This dark magic will fetch it for us if we've
    already signed in.
    """
    oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
    access_token = oauth_provider.extra_data['access_token']
    return access_token


class SetupView(TemplateView):
    """
    The beginning of the OAuth sign-in flow. Logs a user into the kiosk, and saves the token.
    """
    template_name = 'kiosk_setup.html'


@method_decorator(login_required, name='dispatch')
class DoctorWelcome(TemplateView):
    """
    The doctor can see what appointments they have today.
    """
    template_name = 'doctor_welcome.html'

    def make_api_request(self):
        """
        Use the token we have stored in the DB to make an API request and get doctor details. If this succeeds, we've
        proved that the OAuth setup is working
        """
        # We can create an instance of an endpoint resource class, and use it to fetch details
        access_token = get_token()
        api = DoctorEndpoint(access_token)
        # Grab the first doctor from the list; normally this would be the whole practice group, but your hackathon
        # account probably only has one doctor in it.
        return next(api.list())

    def get_context_data(self, **kwargs):
        kwargs = super(DoctorWelcome, self).get_context_data(**kwargs)
        # Hit the API using one of the endpoints just to prove that we can
        # If this works, then your oAuth setup is working correctly.
        doctor_details = self.make_api_request()
        kwargs['doctor'] = doctor_details
        return kwargs

@method_decorator(login_required, name='dispatch')
class DoctorAppointments(View):
    """

    """
    def get(self, request):
        appointments = AppointmentEndpoint(access_token=get_token()).list(date=str(datetime.date.today()))
        filtered_appointments = [
            {
                'id': appointment['id'],
                'patient': appointment['patient'],
                'time': appointment['scheduled_time']
            }
            for appointment in appointments
            if appointment['status'] == ''
        ]
        return render(request, "appointments.html", {"appointments": filtered_appointments})


@method_decorator(login_required, name='dispatch')
class DoctorDashboard(View):
    """

    """
    template_name = 'doctor_dashboard.html'

    def get(self, request):
        return render(request, self.template_name)


@method_decorator(login_required, name='dispatch')
class PatientCheckIn(View):
    """

    """
    patient_form = PatientCheckInForm
    template_name = 'patient_check_in.html'

    def get(self, request, appointment_id, patient_id):
        form = self.patient_form()
        return render(request, self.template_name, {"form": form})

    def post(self, request, appointment_id, patient_id):
        form = self.patient_form(request.POST)
        if form.is_valid():
            patient_details = PatientEndpoint(access_token=get_token()).fetch(patient_id)
            matchers = ('first_name', 'last_name')

            for val in matchers:
                if form.cleaned_data[val].lower() != patient_details[val].lower() and len(patient_details[val]) > 0:
                    form.add_error(val, "Patient info did't match")

            if len(patient_details['social_security_number']) > 0 and form.cleaned_data['social_security_number'] != \
                    patient_details['social_security_number']:
                form.add_error('social_security_number', "Patient info did't match")

            if len(form.errors) == 0:
                return redirect('demographics', appointment_id, patient_id)

        return render(request, self.template_name, {"form": form})


@method_decorator(login_required, name='dispatch')
class PatientDemographics(View):
    """

    """
    patient_demographics = DemographicsForm
    template_name = 'demographics.html'

    def get(self, request, appointment_id, patient_id):
        demographics_details = PatientEndpoint(access_token=get_token()).fetch(patient_id)
        form = self.patient_demographics(initial=demographics_details)
        return render(request, self.template_name, {"form": form})

    def post(self, request, appointment_id, patient_id):
        form = self.patient_demographics(request.POST)

        if form.is_valid():
            try:
                PatientEndpoint(access_token=get_token()).update(patient_id, form.cleaned_data)
                updated_patient_dmg = PatientEndpoint(access_token=get_token()).fetch(patient_id)
                appointment_details = AppointmentEndpoint(access_token=get_token()).fetch(appointment_id)

                #only updating the required fields for making the change status PUT api call
                updated_appointment = {
                    'doctor': appointment_details['doctor'],
                    'duration': appointment_details['duration'],
                    'exam_room': appointment_details['exam_room'],
                    'office': appointment_details['office'],
                    'patient': appointment_details['patient'],
                    'scheduled_time': appointment_details['scheduled_time'],
                    'status': 'Arrived'
                }
                AppointmentEndpoint(access_token=get_token()).update(appointment_id,updated_appointment)
                appointment = Appointment.objects.create(appointment_id=appointment_id)
                appointment.save()
                return render(request, 'finish_check_in.html', {"name": updated_patient_dmg["first_name"]})
            except APIException:
                form.add_error(None, 'Error in updating form. Please try again.')

        return render(
            request,
            self.template_name,
            {
                'form': form,
                'appointment_id': appointment_id,
                'patient_id': patient_id,
            })

