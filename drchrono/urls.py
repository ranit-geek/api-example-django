from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib import admin
from . import views
admin.autodiscover()


urlpatterns = [
    url(r'^setup/$', views.SetupView.as_view(), name='setup'),
    url(r'^welcome/$', views.DoctorWelcome.as_view(), name='setup'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
    url(r'^dashboard/$', views.DoctorDashboard.as_view(), name='dashboard'),
    url(r'^kiosk/$', views.PatientCheckIn.as_view(), name='kiosk'),
]
