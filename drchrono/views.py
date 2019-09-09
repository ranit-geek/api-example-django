
from datetime import datetime
import pytz
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import logout as authentication_logout
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from social_django.models import UserSocialAuth
from django.views.generic import View
from drchrono import utilities
from drchrono.endpoints import DoctorEndpoint, AppointmentEndpoint, PatientEndpoint, CurrentUsersEndpoint
from drchrono.forms import PatientCheckInForm, DemographicsForm
from drchrono.models import Doctor, Appointment, Patient, AverageWaitTime
from drchrono.utilities import save_patient, save_appointment, filter_appointments, save_doctor


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
    The doctor's welcome page which doctors will see after logging in.
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

    def get(self, request, **kwargs):
        doctor_details = self.make_api_request()
        doctor_id = CurrentUsersEndpoint(access_token=get_token()).fetch("")["doctor"]
        save_doctor(get_token(), doctor_id)
        user_timezone = request.COOKIES.get('tzname_from_user')
        filtered_appointments = filter_appointments(get_token(), str(datetime.now(pytz.timezone(user_timezone))), "")
        for appointment in filtered_appointments:
            save_patient(get_token(), appointment["patient"])
            save_appointment(appointment)
        return render(request, self.template_name, {'doctor': doctor_details})


class DoctorAppointments(View):
    """
    This is the starting page of the KIOSK. This page shows all the appointments of a doctor filtered by today's date.
    Patients can start their check in process from here by selecting an appointment slot they have booked.
    """
    template_name = "appointments.html"

    def get(self, request):
        user_timezone = request.COOKIES.get('tzname_from_user')
        filtered_appointments = filter_appointments(get_token(), str(datetime.now(pytz.timezone(user_timezone))), "")
        doctor_id = CurrentUsersEndpoint(access_token=get_token()).fetch("")["doctor"]
        return render(request, self.template_name, {"appointments": filtered_appointments,
                                                     "doctor_id": doctor_id})


class DoctorDashboard(View):
    """
    This page is doctors dashboard page which he can leave open and can see all the appointments filtered by today.
    Doctor can also start seeing a patient and complete seeing a patient from this page.
    """
    template_name = 'doctor_dashboard.html'

    def get(self, request, doctor_id):
        try:
            checked_in_appointments = Appointment.objects.all()
        except ObjectDoesNotExist:
            checked_in_appointments = None
        doctor = Doctor.objects.get(id=doctor_id)
        return render(request, self.template_name, {'checked_in_appointments': checked_in_appointments,
                                                    'doctor': doctor})


class DoctorDashboardUpdate(View):
    """
    This is the part of the doctors dashboard page which is for update. This gets changed whenever a patient checks in.
    """
    template_name = 'dashboard_body.html'

    def get(self, request, doctor_id):
        try:
            checked_in_appointments = Appointment.objects.all()
        except ObjectDoesNotExist:
            checked_in_appointments = None
        doctor = Doctor.objects.get(id=doctor_id)
        return render(request, self.template_name, {'checked_in_appointments': checked_in_appointments,
                                                    'doctor': doctor,
                                                    'status': "success"
                                                    })


class PatientCheckIn(View):
    """
    This page is where patient can confirm their identity by providing specific details.
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
    This is the page where patients can see their demographic information and can also update them.
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

                user_timezone = request.COOKIES.get('tzname_from_user')
                time_now = datetime.now(pytz.timezone('UTC'))
                arrival_time = time_now.astimezone(pytz.timezone(user_timezone))

                appointment_object, created = Appointment.objects.update_or_create(
                    appointment_id=appointment_details['id'],
                    defaults={
                        'status': 'Arrived',
                        'patient': Patient.objects.get(patient_id=appointment_details['patient']),
                        'check_in_time':arrival_time,
                        'scheduled_time':appointment_details['scheduled_time']
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

    """
    This api indicates that doctor has started seeing a patient.This stops the wait time of the patients.
    """
    def post(self, request):
        appointment = Appointment.objects.get(appointment_id=request.POST['appointment_id'])

        if appointment.status == 'Arrived':
            try:
                AppointmentEndpoint(access_token=get_token()).update(request.POST['appointment_id'], {'status': 'In Session'})
                tz_info = appointment.check_in_time.tzinfo
                time_now = datetime.now(tz_info)
                total_wait_time = time_now - appointment.check_in_time
                Appointment.objects.filter(appointment_id=request.POST['appointment_id']).update(status='In Session',
                                                                                                 wait_time=total_wait_time,
                                                                                                 session_start_time=time_now
                                                                                                 )
                return JsonResponse({"msg": "success"})

            except APIException:
                return JsonResponse({"msg": "fail"})
        return JsonResponse({"msg": "fail"})


class CompleteAppointments(APIView):
    """
    This api indicates that doctor has completed his session with the patient.
    """
    def post(self, request):
        appointment = Appointment.objects.get(appointment_id=request.POST['appointment_id'])

        if appointment.status == 'In Session':
            try:
                AppointmentEndpoint(access_token=get_token()).update(request.POST['appointment_id'], {'status': 'Complete'})
                tz_info = appointment.check_in_time.tzinfo
                Appointment.objects.filter(appointment_id=request.POST['appointment_id']).update(status='Complete',
                                                                                                 session_end_time=datetime.now(tz_info))
                return JsonResponse({"msg": "success"})

            except APIException:
                return JsonResponse({"msg": "fail"})


class CalculateWaitTime(View):
    """
    This page calculates the wait time for patients and shows statistics details.
    """

    template_name = 'charts.html'

    def get(self,request, doctor_id):
        user_timezone = request.COOKIES.get('tzname_from_user')
        utilities.calculate_average_wait_time(doctor_id, user_timezone)
        wait_time_data = AverageWaitTime.objects.filter(doctor=doctor_id)
        doctor = Doctor.objects.get(id=doctor_id)
        res_dict = {
            "date_list": [obj.date for obj in wait_time_data],
            "avg_list": [obj.average_wait_time for obj in wait_time_data],
            "doctor": doctor
        }

        if request.is_ajax():
            return JsonResponse({
                "date_list": res_dict["date_list"],
                "avg_list": res_dict["avg_list"]

            })
        return render(request, self.template_name, res_dict)


class Logout(View):
    """Logs out user"""

    def get(self, request):
        authentication_logout(request)
        return redirect('setup')
