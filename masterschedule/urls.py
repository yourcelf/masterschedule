from django.shortcuts import redirect
from django.conf.urls import patterns, include, url
from django.contrib import admin
from vanilla import TemplateView

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/profile/$', lambda *args: redirect("conferences")),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^support/$', TemplateView.as_view(template_name="support.html"), name='support'),
    url(r'', include('schedule.urls')),
)
