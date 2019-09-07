from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib import admin
from . import views
admin.autodiscover()


urlpatterns = [
    url(r'^$', views.SetupView.as_view(), name='setup'),
    url(r'^welcome/$', login_required(views.DoctorWelcome.as_view()), name='welcome'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
    url(r'^dashboard/$', login_required(views.DoctorDashboard.as_view()), name='dashboard'),
    url(r'^patient_check_in/(\d+)/(\d+)$', login_required(views.PatientCheckIn.as_view()), name='patient_check_in'),
    url(r'^appointments/$', login_required(views.DoctorAppointments.as_view()), name='appointments'),
    url(r'^demographics/(\d+)/(\d+)$', login_required(views.PatientDemographics.as_view()), name='demographics'),
    url(r'^logout/$', login_required(views.Logout.as_view()), name='logout'),
    url(r'^start_appointment/$', login_required(views.StartAppointments.as_view()), name='start_appointment'),
    url(r'^complete_appointment/$', login_required(views.CompleteAppointments.as_view()), name='complete_appointment'),

]
