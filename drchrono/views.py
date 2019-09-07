import datetime

from django.core.checks import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import logout as authentication_logout
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from social_django.models import UserSocialAuth
from django.views.generic import View
from drchrono.endpoints import DoctorEndpoint, AppointmentEndpoint, PatientEndpoint, CurrentUsersEndpoint
from drchrono.forms import PatientCheckInForm, DemographicsForm
from drchrono.models import Doctor, Appointment, Patient


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
        doctor_id = CurrentUsersEndpoint(access_token=get_token()).fetch("")["doctor"]
        Doctor.objects.get_or_create(id=doctor_id)
        kwargs['doctor'] = doctor_details
        return kwargs


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


class DoctorDashboard(View):
    """

    """
    template_name = 'doctor_dashboard.html'

    def get(self, request):
        try:
            checked_in_appointments = Appointment.objects.all()
        except ObjectDoesNotExist:
            checked_in_appointments = None
        return render(request, self.template_name, {'checked_in_appointments': checked_in_appointments})


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


class PatientDemographics(View):
    """

    """
    patient_demographics = DemographicsForm
    template_name = 'demographics.html'

    def get(self, request, appointment_id, patient_id):
        demographics_details = PatientEndpoint(access_token=get_token()).fetch(patient_id)
        form = self.patient_demographics(initial=demographics_details)
        return render(request, self.template_name, {"form": form,
                                                    "patient_details": demographics_details})

    def post(self, request, appointment_id, patient_id):
        form = self.patient_demographics(request.POST)

        if form.is_valid():
            try:
                PatientEndpoint(access_token=get_token()).update(patient_id, form.cleaned_data)
                updated_patient_dmg = PatientEndpoint(access_token=get_token()).fetch(patient_id)
                patient_object, created = Patient.objects.update_or_create(
                    patient_id=updated_patient_dmg['id'],
                    defaults={
                        'gender': updated_patient_dmg['gender'],
                        'doctor_id': updated_patient_dmg['doctor'],
                        'first_name': updated_patient_dmg['first_name'],
                        'last_name':updated_patient_dmg['last_name'],
                        'email':updated_patient_dmg['email'],
                        'patient_photo': updated_patient_dmg['patient_photo']
                    }
                )

                appointment_details = AppointmentEndpoint(access_token=get_token()).fetch(appointment_id)

                # only updating the required fields for making the change status PUT api call

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

                appointment_object, created = Appointment.objects.update_or_create(
                    appointment_id=appointment_details['id'],
                    defaults={
                        'status': 'Arrived',
                        'patient': Patient.objects.get(patient_id=appointment_details['patient'])
                    }
                )

                return render(request, 'finish_check_in.html', {"patient": updated_patient_dmg})
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


class StartAppointments(APIView):

    def post(self, request):
        appointment = Appointment.objects.get(appointment_id=request.POST['appointment_id'])

        if appointment.status == 'Arrived':
            try:
                AppointmentEndpoint(access_token=get_token()).update(request.POST['appointment_id'], {'status': 'In Session'})
                tz_info = appointment.check_in_time.tzinfo
                total_wait_time = datetime.datetime.now(tz_info) - appointment.check_in_time
                print appointment.check_in_time
                print datetime.datetime.now(tz_info)
                print total_wait_time
                Appointment.objects.filter(appointment_id=request.POST['appointment_id']).update(status='In Session',
                                                                                                 wait_time=total_wait_time
                                                                                                 )

                return JsonResponse({"msg": "success"})

            except APIException:
                return JsonResponse({"msg": "fail"})
        return JsonResponse({"msg": "fail"})


class CompleteAppointments(APIView):

    def post(self, request):
        appointment = Appointment.objects.get(appointment_id=request.POST['appointment_id'])

        if appointment.status == 'In Session':
            try:
                AppointmentEndpoint(access_token=get_token()).update(request.POST['appointment_id'], {'status': 'Complete'})
                Appointment.objects.filter(appointment_id=request.POST['appointment_id']).update(status='Complete')
                return JsonResponse({"msg": "success"})

            except APIException:
                return JsonResponse({"msg": "fail"})


class Logout(View):
    """Logs out user"""

    def get(self, request):
        authentication_logout(request)
        return redirect('setup')
