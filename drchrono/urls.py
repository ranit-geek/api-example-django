from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib import admin
from . import views
admin.autodiscover()


urlpatterns = [
    url(r'^$', views.SetupView.as_view(), name='setup'),
    url(r'^welcome/$', views.DoctorWelcome.as_view(), name='setup'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
    url(r'^dashboard/$', views.DoctorDashboard.as_view(), name='dashboard'),
    url(r'^patient_check_in/(\d+)/(\d+)$', views.PatientCheckIn.as_view(), name='patient_check_in'),
    url(r'^appointments/$', views.DoctorAppointments.as_view(), name='appointments'),
    url(r'^demographics/(\d+)/(\d+)$', views.PatientDemographics.as_view(), name='demographics'),
]
